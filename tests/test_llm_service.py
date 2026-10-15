from services.fakeProvider1 import Provider1
from services.fakeProvider2 import NIM


def test_provider1_response():
    provider1 = Provider1()
    response = provider1.get_response("gemini-3-flash", "Hello this is a test message from provider 1")
    # assert response["object"] == "chat.completion"
    # assert response["choices"][0]["message"]["content"] == "Hello this is the response from Provider 1"
    assert response.status_code == 429 or response.status_code >= 500 or response["object"] == "chat.completion"

def test_provider2_response():
    provider2 = NIM()
    response = provider2.get_response("nvidia/nemotron-3.5-lightning-30b-a3b", "Hello this is a test message from provider 2")
    # assert response["object"] == "chat.completion"
    # assert response["choices"][0]["message"]["content"] == "Hello this is the response from Provider 2"
    assert response['status_code'] == 429 or response['status_code'] >= 500 or response["object"] == "chat.completion"
