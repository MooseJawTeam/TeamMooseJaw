import os
import django
import base64
from datetime import datetime

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "moosejawums.settings")
django.setup()

# Import models
from pdfdocs.models import DocumentTemplate, GeneratedDocument, DocumentSignature
from ums.models import Users

# Get test user and document
user = Users.objects.get(id='test123')
document = GeneratedDocument.objects.get(id=1)

print(f"User: {user.name}")
print(f"Document: {document.title}")

# Create a test signature (base64 encoded data)
signature_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAZAAAAC" + \
                "WCAYAAADQBiXRAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAALEgAA" + \
                "CxIB0t1+/AAAADh0RVh0U29mdHdhcmUAbWF0cGxvdGxpYiB2ZXJzaW" + \
                "9uMy4xLjEsIGh0dHA6Ly9tYXRwbG90bGliLm9yZy8QZhcZAAAgAElE" + \
                "QVRD9XmbX7dl17Hkd0REZu5z7vfdbrVaakktIQGSEAgwGGzA4DE2Ho" + \
                "Yx9oDHHnjw0IP+FX3og/8CPw82GMcDtjG2AYMBgSUhhNSt7tb9vvee" + \
                "vTMj/CAya+/zfq+kVrdyV1fVrbp16+w9MyIjIyKXiReH8T9ARERERq" + \
                "T/AB8iIiIiIiIiIiIiIiIiIiIiIiIiIiLyH+Ajys/2xyOz9J+lpuOM" + \
                "kRmRETlGZnhmFKOZI1mypEplQamVWJWsJVZLpNZDrYU6HPl4oOf+b7" + \
                "d/3X78v/TvD/kf/3f/LjHGP/t/+/C/z3xm5Nuzs47yiWZRwSLEOWO5" + \
                "MJZnx/LMyHI2lmfG+jRZnxrrs2S5cJbnKctzY70wlgtx8jhZnsDylO" + \
                "R6ZCzXoL9EXE1ywSRvRL82+r3Re6FfFfoAHCbHXeN4p/HeePfecXu78"


# Create a signature in the database
signature = DocumentSignature.objects.create(
    document=document,
    user=user,
    signature_data=signature_data,
    timestamp=datetime.now()
)

print(f"Signature created with ID: {signature.id}")
print(f"Timestamp: {signature.timestamp}")

# Check if the user has signed this document
has_signed = DocumentSignature.objects.filter(document=document, user=user).exists()
print(f"User has signed document: {has_signed}")

# List all signatures for this document
all_signatures = DocumentSignature.objects.filter(document=document)
print(f"Total signatures for document: {all_signatures.count()}")

for sig in all_signatures:
    print(f"Signature by: {sig.user.name}, at: {sig.timestamp}, valid: {sig.is_valid}")