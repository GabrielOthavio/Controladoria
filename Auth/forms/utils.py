from django import forms

ALLOWED_TAGS = ['b', 'i', 'u', 'p', 'br', 'strong', 'em', 'li', 'ul', 'ol']


def validate_cpf(value):
    digits = ''.join(filter(str.isdigit, value or ''))

    if len(digits) != 11:
        raise forms.ValidationError("CPF deve conter 11 dígitos.")
    if len(set(digits)) == 1:
        raise forms.ValidationError("CPF inválido.")

    # Primeiro dígito verificador
    total = sum(int(digits[i]) * (10 - i) for i in range(9))
    first = (total * 10) % 11
    if first >= 10:
        first = 0
    if first != int(digits[9]):
        raise forms.ValidationError("CPF inválido.")

    # Segundo dígito verificador
    total = sum(int(digits[i]) * (11 - i) for i in range(10))
    second = (total * 10) % 11
    if second >= 10:
        second = 0
    if second != int(digits[10]):
        raise forms.ValidationError("CPF inválido.")

    return digits
