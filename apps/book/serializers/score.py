from rest_framework import serializers


class ScoreSerializer(serializers.Serializer):
    book_id = serializers.IntegerField(required=False)
    rating = serializers.IntegerField(min_value=1, max_value=5, required=False)


"""
Serializer for validating and deserializing data related to scores (reviews) for books.
This serializer is used to handle the data input for adding or updating book scores.

    - Type: Integer
    - `required=False`: This field is optional, meaning it can be omitted from the input data.
    
    - Type: Integer
    - `min_value=1`: The rating must be at least 1.
    - `max_value=5`: The rating must not exceed 5.
    - `required=False`: This field is optional, meaning it can be omitted from the input data.
"""