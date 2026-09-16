import threading


class Entry:
    """Store'daki her key'in kutusu. Her kutu bir tip ve bir değer taşir."""

    def __init__(self, type_: str, value):
        self.type: str = type_
        self.value = value


class Store:
    """Ham veri saklama. Komut mantiği commands/ klasöründeki dosyalarda."""

    def __init__(self):
        self.data: dict[str, Entry] = {}
        self.lock = threading.Lock()

    def get_entry(self, key: str) -> Entry | None:
        return self.data.get(key)

    def set_entry(self, key: str, entry: Entry) -> None:
        self.data[key] = entry

    def delete_entry(self, key: str) -> bool:
        if key in self.data:
            del self.data[key]
            return True
        return False