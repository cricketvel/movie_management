import datetime, json




class Convert(object):

    def __init__(self, value, datatype):
        datatypes = {"string":"str", "integer":"int"}
        self.value = value
        self.datatype = datatypes.get(datatype, datatype)
        self.converted_data = value
        self.convert()

    def convert(self):
        meth = getattr(self, "convert_to_{0}".format(self.datatype.lower()))
        try:
            value = meth()
            self.converted_data = value
        except ValueError as exc:
            self.converted_data = self.value


    def convert_to_dumps(self):
        return json.dumps(self.value)


    def convert_to_utf_decode(self):
        return self.value.decode("utf-8") if isinstance(self.value, bytes) else self.value


    def convert_to_str(self):
        return str(self.value)


    def convert_to_datetime(self):
        data = datetime.datetime.strptime(self.value, "%Y-%m-%dT%H:%M:%S.%fZ")
        return data


    def convert_to_boolean(self):
        true_list = ['true', 'True', '1', 1]
        false_list = ['false', 'False', '0', 0]
        if self.value in true_list:
            return True
        elif self.value in false_list:
            return False
        else:
            return bool(self.value)


    def convert_to_int(self):
        return int(self.value)


    def convert_to_float(self):
        return float(self.value)


    def convert_to_list(self):
        return list(self.value)


    def convert_to_dict(self):
        return dict(self.value)


    @property
    def get_value(self):
        return self.converted_data
