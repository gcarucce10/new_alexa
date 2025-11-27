import json
import os

from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv("server.env", override=True)  

class ActionsServer:
    def __init__(self):
        try:
            # Usa caminho relativo ao arquivo atual para localizar o JSON de config
            base_dir = os.path.dirname(__file__)
            config_path = os.path.join(base_dir, 'action_config.json')
            # alternativa: config_path = os.path.join(base_dir, 'server_config.json')
            with open(config_path, 'r', encoding='utf-8') as config_file:
                self.config: dict = json.load(config_file)
        except FileNotFoundError:
            print(f"Error: Configuration file not found at {config_path}.")
            self.config = None
        except json.JSONDecodeError:
            print("Error: Configuration file is not a valid JSON.")
            self.config = None
        except Exception as e:
            print(f"Unexpected error: {e}")
            self.config = None

    @staticmethod
    def read_file_as_string(file_path, encoding="utf-8"):
        """
        Reads the entire content of a text file and returns it as a string.
        """
        try:
            with open(file_path, "r", encoding=encoding) as file:
                return file.read()
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
        except UnicodeDecodeError:
            print(f"Error: Could not decode file '{file_path}' with encoding '{encoding}'.")
        except Exception as e:
            print(f"Unexpected error: {e}")
        return None    

    def get_action_atributes(self):
        """
        Send the action attributes as a dictionary to the IA Server
        If not loaded, return None
        """
        if self.config:
            
            instructions = self.read_file_as_string("action_instructions.txt")

            if instructions is None:
                print("Error: Could not read action instructions.")
                return None
            
            action_atributes = {'name': self.config['name'], 
                            'description': self.config['description'],
                            'instructions': instructions, 'version': self.config['version']}
            return action_atributes
        
        else:
            print("Error: Configuration not loaded.")
            return None
        
    def perform_action(self, params: dict) -> str:  
        pass

    def parse_reminders(self, reminders: dict | list[dict]):
        """
        Lê e padroniza os lembretes para enviar para o client 
        """

        reminders_payload = []

        if isinstance(reminders, dict):
            frequency = reminders.get("frequency", "once")
            time = reminders.get("time", None)
            message = reminders.get("message", None)
            reminders_payload = [{"frequency": frequency, "time": time, "message": message}]

        if isinstance(reminders, list):
            for r in reminders:
                if not isinstance(r, dict):
                    raise ValueError("Each reminder must be a dictionary.")
                frequency = r.get("frequency", "once")
                time = r.get("time", None)
                message = r.get("message", None)

                reminders_payload.append({"frequency": frequency, "time": time, "message": message})

                if time is None or message is None:
                    raise ValueError("Each reminder must have 'time' and 'message' fields.")
                
        return reminders_payload
    
    def get_reminders() -> list:
        pass

    def flask_server(self):
        app = Flask(__name__)

        @app.route('/action_attributes', methods=['GET'])
        def action_attributes():
            attributes = self.get_action_atributes()
            if attributes:
                return jsonify(attributes), 200
            else:
                return jsonify({"error": "Configuration not loaded"}), 500

        @app.route('/perform_action', methods=['POST'])
        def perform_action_route():
            data = request.json.get('param', {})
            
            result, resource = self.perform_action(data)
            return jsonify({'result': result, 'resource': resource}), 200
        
        @app.route('/health_check', methods=['GET'])
        def health_check():
            return jsonify({"Version": self.config['version']}), 200
        
        @app.route('/get_reminders', methods=['GET'])
        def get_reminders_route():
            return jsonify(self.parse_reminders(self.get_reminders())), 200
            
        
        app.run(host=os.getenv("IP", "0.0.0.0"), port=int(os.getenv("PORT", 5000)))