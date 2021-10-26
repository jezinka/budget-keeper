import re


def clean_content(content):
    content = re.sub(r'<head>.*</head>', '', content, flags=re.DOTALL)
    content = re.sub(r'<style.*?>.*</style>', '', content, flags=re.DOTALL)
    content = re.sub(r'<.*?>', '', content, flags=re.DOTALL)
    content = re.sub(r'\(https?://.*?\)', '', content, flags=re.DOTALL)
    content = re.sub(r'https?://.*? ', '', content, flags=re.DOTALL)
    content = re.sub(r'[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}', '', content, flags=re.DOTALL)
    content = re.sub(r"([a-złążźęćóśń])([A-Z0-9])", r"\1 \2", content)
    content = re.sub(r"(.)\1{3,}", r"\1", content)
    content = re.sub(r'\u00A0', ' ', content)
    content = re.sub(r'&nbsp;', ' ', content)
    content = re.sub(r'&zwnj;', ' ', content)
    content = re.sub(r'	', ' ', content)
    content = re.sub(r'[^a-ząęńćśżźółA-ZĄĘŃĆŚŻŹÓŁ\s]', ' ', content)
    content = re.sub(r'\s{2,}', ' ', content)
    content = re.sub(r'\n', ' ', content)
    return content


def process_body(content):
    clean_c = set(map(lambda x: x.lower(), filter(lambda x: len(x) > 2, clean_content(content).split(' '))))
    return clean_c
