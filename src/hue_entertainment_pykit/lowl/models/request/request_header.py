class RequestHeader:
    def __init__(self, hue_application_key: str | None = None):
        self.__content_type: str = "application/json"
        self.__hue_application_key: str = hue_application_key

    def get_content_type(self):
        return self.__content_type

    def get_hue_application_key(self):
        return self.__hue_application_key

    def set_hue_application_key(self, hue_application_key: str):
        self.__hue_application_key = hue_application_key

    def get_data(self):
        return {
            "Content-Type": self.__content_type,
            "hue-application-key": self.__hue_application_key,
        }
