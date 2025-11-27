import actions_server

class DiceAction(actions_server.ActionsServer):
    def __init__(self):
        super().__init__()

    def perform_action(self, params: dict) -> dict:

        sides = int(params.get('sides', None))

        if sides is None:
            return {"error": "Número de lados não especificado."}
        
        result = self.dice_roll(sides)
        return {"result": result}

    def dice_roll(self, sides: int = 6) -> int:
        """
        Simula o lançamento de um dado com o número especificado de lados.
        
        :param sides: Número de lados do dado (padrão: 6)
        :return: Resultado do lançamento
        """
        import random

        if sides < 2:
            raise ValueError("O número de lados deve ser pelo menos 2.")

        return random.randint(1, sides)
    
if __name__ == "__main__":
    dice_server = DiceAction()
    dice_server.flask_server()
    