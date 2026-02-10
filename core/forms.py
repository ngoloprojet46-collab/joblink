from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User
from .models import Service
from django import forms


from django import forms
from .models import Abonnement

class PreuvePaiementForm(forms.ModelForm):
    class Meta:
        model = Abonnement
        fields = ['preuve_paiement']



from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import User


class UserRegisterForm(UserCreationForm):

    ROLE_CHOICES = [
        ('prestataire', 'Prestataire'),
        ('demandeur', 'Demandeur'),
    ]

    SOURCE_CHOICES = [
        ('facebook', 'Facebook'),
        ('whatsapp', 'WhatsApp'),
        ('ami', 'Recommandation d’un ami'),
        ('ecole', 'École / Université'),
        ('tiktok', 'TikTok'),
        ('autre', 'Autre'),
    ]

    AVIS_CHOICES = [
        ('excellent', 'Excellent'),
        ('bon', 'Bon'),
        ('moyen', 'Moyen'),
        ('mauvais', 'Mauvais'),
    ]

    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect)
    phone = forms.CharField(label="Téléphone", required=True)

    # 🔥 Nouveaux champs
    source = forms.ChoiceField(
        choices=SOURCE_CHOICES,
        label="Où avez-vous entendu parler de JobLink ?",
        required=False
    )

    avis_plateforme = forms.ChoiceField(
        choices=AVIS_CHOICES,
        label="Comment trouvez-vous la plateforme ?",
        required=False
    )

    suggestion = forms.CharField(
        widget=forms.Textarea(attrs={'rows':3}),
        required=False,
        label="Suggestions (facultatif)"
    )

    password1 = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True
    )

    password2 = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'phone',
            'role',
            'photo',
            'source',
            'avis_plateforme',
            'suggestion',
            'password1',
            'password2',
        ]

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 != password2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas")

        return password2

class ProfilUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'photo']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

        help_texts = {
            'username': '',
            'email': '',
        }


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class':'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class':'form-control password-field'})
    )


class ServiceForm(forms.ModelForm):
    image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    video = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Service
        fields = ['titre', 'description', 'categorie', 'ville', 'telephone', 'adresse', 'prix', 'image', 'video']
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titre du service'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Décrivez votre service'
            }),
            'categorie': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex : Mécanique, Jardinage, Cours à domicile'
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre numéro de telephone'
            }),

            'adresse': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Adresse du service (ex: Bouaké au commerces)'
            }),

            'prix': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Prix en FCFA'
            }),
        }


from django import forms
from .models import Avis, Boutique

class AvisForm(forms.ModelForm):
    class Meta:
        model = Avis
        fields = ['nom', 'message']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Votre commentaire'}),
        }

class BoutiqueForm(forms.ModelForm):
    class Meta:
        model = Boutique
        fields = ['nom', 'description', 'categorie', 'image']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de la boutique'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Description de la boutique'
            }),
            'categorie': forms.Select(attrs={
                'class': 'form-control'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'   # 🔥 limite le choix aux images
            }),
        }

    # 🔒 Sécurité backend (empêche vidéos)
    def clean_image(self):
        image = self.cleaned_data.get('image')

        if image:
            if not image.content_type.startswith('image'):
                raise forms.ValidationError(
                    "Vous devez télécharger uniquement une image."
                )

        return image

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import SetPasswordForm

class ResetPasswordForm(forms.Form):
    username = forms.CharField(label="Nom d'utilisateur")
    new_password1 = forms.CharField(widget=forms.PasswordInput, label="Nouveau mot de passe")
    new_password2 = forms.CharField(widget=forms.PasswordInput, label="Confirmer le mot de passe")

    def clean(self):
        cleaned_data = super().clean()
        pwd1 = cleaned_data.get("new_password1")
        pwd2 = cleaned_data.get("new_password2")

        if pwd1 != pwd2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas")
        
        return cleaned_data


