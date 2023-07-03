import pickle
class ClearStoredCallsigns():
    def __init__(self, cached_callsign_path:str) -> None:
        callsign_file = open(cached_callsign_path, "wb")
        pickle.dump([], callsign_file)
        callsign_file.close()

if __name__ == "__main__":
    clear = ClearStoredCallsigns()