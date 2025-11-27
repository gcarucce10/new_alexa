import requests
import json
import os

_ACTIONS_CONFIG_FILE = "actions_config.json"
_ACTIONS_ATTRIBUTES_ENDPOINT = "/action_attributes"
_ACTIONS_PERFORM_ENDPOINT = "/perform_action"
_ACTIONS_CONFIG_HEALTH_ENDPOINT = "/health_check"


class RemoteActionConnector:
    def __init__(self):

        try:
            # Usa caminho relativo ao arquivo atual para localizar o JSON de config
            base_dir = os.path.dirname(__file__)
            config_path = os.path.join(base_dir, _ACTIONS_CONFIG_FILE)
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
    

    def reload_json_config(self):
        """
        Reloads the JSON configuration file to update the action settings.
        """
        try:
            # Usa caminho relativo ao arquivo atual para localizar o JSON de config
            base_dir = os.path.dirname(__file__)
            config_path = os.path.join(base_dir, _ACTIONS_CONFIG_FILE)
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


    def save_json_config(self):
        """
        Saves the current configuration back to the JSON file.
        """
        try:
            # Usa caminho relativo ao arquivo atual para localizar o JSON de config
            base_dir = os.path.dirname(__file__)
            config_path = os.path.join(base_dir, _ACTIONS_CONFIG_FILE)
            with open(config_path, 'w', encoding='utf-8') as config_file:
                json.dump(self.config, config_file, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving configuration: {e}")


    def get_status_code(self) -> int:
        """
        Returns the status code from the last action request.

        :return: Status code as an integer.
        """
        return self.status_code
    
    def get_status_json(self) -> dict:
        """
        Returns the JSON response from the last action request.

        :return: JSON response as a dictionary.
        """
        return self.response_json
    

    def send_action_request(self, params: list[str] | dict, action_name: str = None) :
        """
        Sends a POST request to the action server with the given parameters.

        :params: List of parameters to send to the action server.
                 Can be a dictionary or a list of strings.
        :return: The response from the action server.
        """

        if action_name is None:
            action_name = params[0]

        # Find the endpoint URL for the specified action
        for action in self.config.get("actions", []):
            if action.get("name") == action_name:
                url_post = action.get("endpoint")
                break

        # Error Handling: Action not found
        if url_post is None:
            print(f"Error: Action '{action_name}' not found in configuration.")
            return None

        url_post: str = url_post + _ACTIONS_PERFORM_ENDPOINT

        if params == dict:
            format_params = params
        else:
            format_params = self.format_json(params)
        data = {"param": format_params}

        # TODO : Insert more data like session ID, user ID, etc

        result = self.send_json_post(url_post, data)

        self.status_code = result.status_code if result else None
        self.response_json = result.json() if result else None

        return self.response_json 
    
    
    def format_json(self, list_params: list[str]) -> dict:
        """
        Formats a list of string parameters into a JSON-compatible dictionary.

        - param list_params: List of string parameters.
            ([ActionName] [--[KEY] [VALUE]*]*) | [--[KEY] [VALUE]*]*
        - return: Dictionary formatted for JSON.
        """
        # Remove Action Name if exists
        if list_params[0].startswith("--") == False:
            params = list_params[1:] # Exclude the first element which is the action name
        else:
            params = list_params

        json_data = {}
        values = []
        is_key = True # Key == True, Value == False

        for index in range(len(params)):

            param = params[index]

            # Is Key
            if is_key:
                param = param.removeprefix("--")
                key = param
                is_key = False

            # Is Value
            else:

                # Value is a list
                if param.endswith(","):
                    param = param.removesuffix(",")
                    values.append(param)

                # Single value or last value in list
                else:
                    values.append(param)
                    if values.__len__() == 1:
                        # Single value, add directly
                        json_data[key] = values[0]
                    else:
                        # Multiple values, add as list
                        json_data[key] = values

                    # Reset for next key-value pair
                    values = []  
                    is_key = True  

        return json_data


    def get_action_attributes(self, url, save=True) -> dict:
        """
        Sends a GET request to retrieve action attributes from the action server.
        If the action already exists in the config, updates its description and instructions in RAM.
        If not, create a new entry in the config in RAM.

        :return: The JSON response containing action attributes as a dictionary.
        """

        url_get = url + _ACTIONS_ATTRIBUTES_ENDPOINT

        result = self.get_json_response(url_get)

        if result is None:
            return None

        action_name = result.get("name", None)
        description = result.get("description", None)
        instructions = result.get("instructions", None)
        version = result.get("version", None)

        dict_actions: list[dict] = self.config.get("actions", [])

        update = False

        # If in config and version differ, update
        for action in dict_actions:
            if action.get("name") == action_name:
                if version is not None and action.get("version", None) != version:
                    if description is not None:
                        action["description"] = description
                    if instructions is not None:
                        action["instructions"] = instructions
                    if version is not None:
                        action["version"] = version
                    update = True
                    break
        
        # Not found, create new entry
        if update == False:
            new_action = {
                "name": action_name,
                "description": description,
                "instructions": instructions,
                "version": version,
                "endpoint": url
            }
            dict_actions.append(new_action)
            self.config["actions"] = dict_actions
        
        if save:
            self.save_json_config()

        return result
    

    def check_alive_actions(self) -> list[str]:
        """
        Checks which actions are alive by sending a GET request to each action's health endpoint.

        :return: List of names of alive actions.
        """
        alive_actions = []
        changed = False

        for action in self.config.get("actions", []):
            action_name = action.get("name")
            endpoint = action.get("endpoint")
            version_current = action.get("version", None)
            health_url = endpoint + _ACTIONS_CONFIG_HEALTH_ENDPOINT

            try:
                get_json = self.get_json_response(health_url, timeout=2)

                if get_json is not None:
                    alive_actions.append(action_name)

                    version_on = get_json.get("version", None)
                    if version_on is not None and version_current is not None:

                        # If versions differ, update action attributes
                        if version_on != version_current:
                            self.get_action_attributes(endpoint, save=False)
                            changed = True
                    continue  # If successful, move to next action

            except requests.exceptions.RequestException:
                continue  # If there's an error, the action is considered not alive

        if changed:
            self.save_json_config()

        return alive_actions


    def send_json_post(self, url: str, data: dict) -> requests.Response:
        """
        Sends a POST request with JSON data to the specified URL.

        :param url: The endpoint URL to send the request to.
        :param data: The dictionary to be sent as JSON in the request body.
        :return: The response object from the POST request.
        """
        try:
            response: requests.Response = requests.post(url, json=data)
            response.raise_for_status()  # Raise an error for bad responses (4xx and 5xx)
            return response
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while sending POST request: {e}")
            return None
        

    def get_json_response(self, url: str, timeout = 10) -> dict:
        """
        Sends a GET request to the specified URL and returns the JSON response.

        :param url: The endpoint URL to send the request to.
        :return: The JSON response as a dictionary, or None if an error occurs.
        """
        try:
            response: requests.Response = requests.get(url, timeout=timeout)
            response.raise_for_status()  # Raise an error for bad responses (4xx and 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while sending GET request: {e}")
            return None
        except json.JSONDecodeError:
            print("Error decoding JSON response.")
            return None
        

    def build_instruction_set(self, file_path: str) -> None:
        """
        Builds the instruction set file for active actions.
        """

        active_actions = self.check_alive_actions()
        instructions = ""

        for action in self.config.get("actions", []):
            if action.get("name") in active_actions:
                instructions += action.get("instructions", "") + "\n\n"
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(instructions)
        except IOError as e:
            print(f"An error occurred while writing to the file: {e}")

    

if __name__ == "__main__":
    connector = RemoteActionConnector()
    response = connector.send_action_request(["dice_manager", "--sides", "4"])
    print(response)
    connector.build_instruction_set("test_instructions.txt")
