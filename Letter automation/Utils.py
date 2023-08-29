import config

def select_template(gen_string):
    return config.templates.get(gen_string, {})

def select_pdf(gen_string):
    return config.pdf_mapping.get(gen_string, None)