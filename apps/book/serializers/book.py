from rest_framework import serializers


class BookSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=200)
    author = serializers.CharField(max_length=200)
    genre = serializers.CharField(max_length=50)


"""
Serializer for validating and deserializing data related to books.
This serializer is used to handle the data input and output for book objects.

    - Type: Integer
    - Represents the unique identifier for the book.
    - This field is required and must be an integer.
    
    - Type: String
    - Maximum Length: 200 characters
    - Represents the title of the book.
    - This field is required and must be a string with a maximum length of 200 characters.
    
    - Type: String
    - Maximum Length: 200 characters
    - Represents the name of the author of the book.
    - This field is required and must be a string with a maximum length of 200 characters.
    
    - Type: String
    - Maximum Length: 50 characters
    - Represents the genre or category of the book.
    - This field is required and must be a string with a maximum length of 50 characters.
"""
