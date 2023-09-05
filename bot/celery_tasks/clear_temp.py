import os


def remove_files(uid: str) -> None:
    try:
        os.remove(f"bot/temp/{uid}")
        os.remove(f"bot/temp/{uid}_no_bg.png")
        os.remove(f"bot/temp/{uid}_no_bg.webp")
    except FileNotFoundError as ex:
        pass
