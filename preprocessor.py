def insert_values_into_html(filename: str, values: dict) -> bytes:
	with open(filename, 'r') as f:
		a = f.read()

	buffer_list = []
	buffer = ''
	buffer_in = False

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
	insert_counter = 0
	html_list = []

	for i in range(len(a)):
		if buffer_in:
			if a[i] == '{':
				buffer_in = False
				html_list.append(buffer)
				buffer = ''
				html_list.append(values[buffer_list[insert_counter]])
				insert_counter += 1
			else:
				buffer += a[i]
		else:
			if a[i] == '}':
				buffer_in = True
	else:
		html_list.append(buffer)
		buffer = ''

	result = ''.join(html_list).replace('\n', '\r\n').replace('\t', '')

	return result