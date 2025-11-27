import json
import os


def unite_txt_files(file1: str, file2: str, file3: str, output_file: str) -> None:
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for fname in [file1, file2, file3]:
            with open(fname, 'r', encoding='utf-8') as infile:
                outfile.write(infile.read())
                outfile.write('\n')  # Optional: adds a newline between files

def build_prompt() -> None:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    b_path = os.path.join(current_dir, "begin.txt")
    e_path = os.path.join(current_dir, "end.txt")
    instruction_set = os.path.join(current_dir, "Instruction.txt")
    out_path = os.path.join(current_dir, "Actions_Prompt.txt")
    print("[UPDATE] Atualizando o prompt")
    unite_txt_files(b_path, instruction_set, e_path, out_path)
