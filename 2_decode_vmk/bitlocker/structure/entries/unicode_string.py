class UnicodeString:
    def __init__(self, data, label='UNK') -> None:
        self.label = label
        self.name = data.decode('UTF-16LE').rstrip('\x00')
    def __repr__(self) -> str:
        return f"""Label: {self.label}
    - Unicode string: {self.name}"""