import logging

class RequestPreprocessor:
    _instance = None
    def __new__(cls):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self):
        self.DEBUG = False
        self.logger = logging.Logger("request", logging.INFO)

    def _request_parse(self, request: bytes) -> dict:
        return_dict = {}
        request = request.split('\r\n')
        empty_line_count = 0
        for line in request:
            if self.DEBUG:
                print(line)
            line = line.split(': ')
            if len(line) == 1 and line[0] != '':
                if empty_line_count == 0:
                    line = line[0].split(' ')
                    method, addr, protocol = line[0], line[1], line[2]
                    addr = self._get_url_params(addr)
                    return_dict['METHOD'] = method
                    return_dict['ADDR'] = addr[0]
                    return_dict['PROTOCOL'] = protocol
                    return_dict['PARAMS'] = addr[1]
                else:
                    return_dict['BODY'].append(line)
            elif line[0] == '':
                if empty_line_count == 0:
                    return_dict['BODY'] = []

                empty_line_count += 1
            else:
                if empty_line_count < 1:
                    head, body = line[0], line[1]
                    return_dict[head.upper()] = body
                else:
                    return_dict['BODY'].append(line)

        if return_dict['METHOD'] != 'GET':
            self._parse_post_body(return_dict)

        return return_dict

    def _get_url_params(self, addr: str) -> tuple:
        if '?' in addr:
            params_dict = {}
            addr = addr.split('?')
            params, addr = addr[1].split('&'), addr[0]
            for param in params:
                param = param.split('=')
                head, body = param[0], param[1]
                try:
                    params_dict[head] = int(body)
                except ValueError:
                    if body == 'true':
                        params_dict[head] = True
                    elif body == 'false':
                        params_dict[head] = False
                    else:
                        params_dict[head] = body.replace('%20', ' ')

            return (addr, params_dict)

        return (addr, {})


    def _parse_post_body(self, request: dict):
        if request['CONTENT-TYPE'] == 'application/x-www-form-urlencoded':
            request['BODY'] = '?' + request['BODY'][0][0]
            _, body = self._get_url_params(request['BODY'])
            request['BODY'] = body
        elif request['CONTENT-TYPE'] == 'application/json':
            body = {}
            for line in request['BODY']:
                if line[0] == '{' or line[0] == '}':
                    continue
                else:
                    line[0] = line[0].lstrip().replace('"', '')
                    line[1] = line[1].replace('"', '').replace(',', '')
                    try:
                        if '.' in line[1]:
                            body[line[0]] = float(line[1])
                        else:
                            body[line[0]] = int(line[1])
                    except ValueError:
                        body[line[0]] = line[1]

            request['BODY'] = body

    def __call__(self, request: bytes) -> dict:
        return self._request_parse(request)