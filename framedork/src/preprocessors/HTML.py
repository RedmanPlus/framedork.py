class HTMLPreprocessor:

    def __call__(self, filename: str, values: dict) -> str:
        return self._insert_values_into_html(filename, values)


    def _insert_html_into_html(self, parent_file: str, child_file: str) -> str:
        with open(parent_file, 'r') as f:
            parent = f.read()

        with open(child_file, 'r') as f:
            child = f.read()

        child_lines = child.split('\n')
        blocks = {}
        current_block = ''
        block_buffer = ''
        is_block = False
        for i, line in enumerate(child_lines):
            if line.startswith('{%') and line.endswith('%}'):
                contents = line.split(' ')
                if not is_block:
                    if contents[1] == 'block':
                        current_block = contents[2]
                        is_block = True
                        continue
                else:
                    if contents[1] == 'endblock':
                        blocks[current_block] = block_buffer
                        current_block = ''
                        block_buffer = ''
                        is_block = False
            if is_block:
                block_buffer += line

        parent_lines = parent.split('\n')
        parent_list = []
        for line in parent_lines:
            if (line.replace('\t', '')).startswith('{%') and (line.replace('\t', '')).endswith('%}'):
                contents = line.split(' ')
                parent_list.append(blocks[contents[2]])
                continue
            parent_list.append(line)

        result = ''.join(parent_list)

        return result


    def _extend_html(self, filename: str) -> str:
        with open(filename, 'r') as f:
            html = f.read()

        html = html.split('\n')
        if html[0].startswith('{%') and html[0].endswith('%}'):
            contents = html[0].split(' ')
            result = self._insert_html_into_html(contents[2].replace("'", ""), filename)
        else:
            result = ''.join(html)

        return result


    def _insert_values_into_html(self, filename: str, values: dict) -> str:
        a = self._extend_html(filename)

        buffer_list: list = []
        buffer: str = ''
        buffer_in: bool = False

        for i in range(len(a)):
            if not buffer_in:
                if a[i] == '{':
                    a.replace('{', '', 1)
                    buffer_in = True
            else:
                if a[i] == '}':
                    a.replace('}', '', 1)
                    buffer_in = False
                    buffer_list.append(buffer.strip())
                    buffer = ''
                    continue
                buffer += a[i]

        buffer_in = True
        insert_counter: int = 0
        html_list: list = []

        for i in range(len(a)):
            if buffer_in:
                if a[i] == '{':
                    buffer_in = False
                    html_list.append(buffer)
                    buffer = ''
                    html_list.append(str(values[buffer_list[insert_counter]]))
                    insert_counter += 1
                else:
                    buffer += a[i]
            else:
                if a[i] == '}':
                    buffer_in = True
        else:
            html_list.append(buffer)
            buffer = ''

        result: str = ''.join(html_list).replace('\n', '\r\n').replace('\t', '')

        return result
