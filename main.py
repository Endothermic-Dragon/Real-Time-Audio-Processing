from diffie_hellman import DiffieHellman
from chaos_keys import ChaosKeys
import asyncio

def user_1():
  from audio_record import run as record_run
  input_dict = {}
  with open("./key_exchange/public_all.txt", "r", encoding="utf-8") as f:
    data = f.readline().strip()
    while data != "":
      input_dict[data.split("=")[0]] = int(data.split("=")[1])
      data = f.readline().strip()

  for i in range(1, 4):
    with open(f"./key_exchange/user_1_{i}.txt", "r", encoding="utf-8") as f:
      data = f.readline().strip()
      while data != "":
        input_dict[f"{data.split('=')[0]}_{i}"] = int(data.split("=")[1])
        data = f.readline().strip()

    input_dict[f"shared_secret_{i}"] = pow(
        input_dict[f"df_encoded_recieved_{i}"], input_dict[f"private_exponent_{i}"],
        input_dict["modulus"]
    )

  print("Shared secret 1:", input_dict["shared_secret_1"])
  print("Shared secret 2:", input_dict["shared_secret_2"])
  print("Shared secret 3:", input_dict["shared_secret_3"])

  chaos_keys = ChaosKeys(
      input_dict["min_key_length"], input_dict["max_key_length"], input_dict["modulus"],
      input_dict["shared_secret_1"], input_dict["shared_secret_2"],
      input_dict["shared_secret_3"]
  ).generage_keys()

  asyncio.run(record_run(chaos_keys))
  print(1)

def user_2():
  from audio_play import run as play_run
  input_dict = {}
  with open("./key_exchange/public_all.txt", "r", encoding="utf-8") as f:
    data = f.readline().strip()
    while data != "":
      input_dict[data.split("=")[0]] = int(data.split("=")[1])
      data = f.readline().strip()

  for i in range(1, 4):
    with open(f"./key_exchange/user_2_{i}.txt", "r", encoding="utf-8") as f:
      data = f.readline().strip()
      while data != "":
        input_dict[f"{data.split('=')[0]}_{i}"] = int(data.split("=")[1])
        data = f.readline().strip()

    input_dict[f"shared_secret_{i}"] = pow(
        input_dict[f"df_encoded_recieved_{i}"], input_dict[f"private_exponent_{i}"],
        input_dict["modulus"]
    )

  print("Shared secret 1:", input_dict["shared_secret_1"])
  print("Shared secret 2:", input_dict["shared_secret_2"])
  print("Shared secret 3:", input_dict["shared_secret_3"])

  chaos_keys = ChaosKeys(
      input_dict["min_key_length"], input_dict["max_key_length"], input_dict["modulus"],
      input_dict["shared_secret_1"], input_dict["shared_secret_2"],
      input_dict["shared_secret_3"]
  ).generage_keys()

  asyncio.run(play_run(chaos_keys))

  chaos_keys = ChaosKeys(
      input_dict["min_key_length"], input_dict["max_key_length"], input_dict["modulus"],
      input_dict["shared_secret_1"], input_dict["shared_secret_2"],
      input_dict["shared_secret_3"]
  ).generage_keys()

match int(input("""Pick one of the following:
Set up shared secrets (must run first) - 0
User 1 (stream) - 1
User 2 (receive) - 2
> """)):
  case 0:
    user_input = input("Minimum key length (default 16384): ").strip()
    min_key_length = 16384
    if user_input != "":
      min_key_length = int(user_input)

    user_input = input("Maximum key length (default 32768): ").strip()
    max_key_length = 32768
    if user_input != "":
      max_key_length = int(user_input)

    DiffieHellman().generate_keys(min_key_length, max_key_length)
  case 1:
    user_1()
  case 2:
    user_2()
  # case 3:
  #   user_1()
  #   user_2()
  #   input()
