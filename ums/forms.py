from django import forms
from .models import TermWithdrawalForm

class TermWithdrawalFormForm(forms.ModelForm):
    class Meta:
        model = TermWithdrawalForm
        fields = [
            'myuh_id', 'phone_number', 'program_plan', 'academic_career',
            'withdrawal_term', 'withdrawal_year',
            'financial_aid_acknowledged', 'international_student_acknowledged',
            'student_athlete_acknowledged', 'veteran_acknowledged',
            'graduate_student_acknowledged', 'doctoral_student_acknowledged',
            'housing_acknowledged', 'dining_services_acknowledged',
            'parking_acknowledged', 'final_acknowledgment',
            'signature_data', 'signature_date'
        ]
        widgets = {
            'myuh_id': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'program_plan': forms.TextInput(attrs={'class': 'form-control'}),
            'academic_career': forms.TextInput(attrs={'class': 'form-control'}),
            'withdrawal_term': forms.Select(attrs={'class': 'form-control'}),
            'withdrawal_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'signature_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'signature_data': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make checkboxes required
        for field_name in [
            'financial_aid_acknowledged', 'international_student_acknowledged',
            'student_athlete_acknowledged', 'veteran_acknowledged',
            'graduate_student_acknowledged', 'doctoral_student_acknowledged',
            'housing_acknowledged', 'dining_services_acknowledged',
            'parking_acknowledged', 'final_acknowledgment'
        ]:
            self.fields[field_name].required = True 