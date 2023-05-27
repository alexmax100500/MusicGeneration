import pathlib
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from musicbot.musicautobot.multitask_transformer.transform import MultitrackItem
from .forms import UploadFileForm
from django.shortcuts import render

from django.http import HttpResponse, HttpResponseNotFound, JsonResponse

from rest_framework.decorators import api_view
from musicbot.musicautobot.config import multitask_config
from musicbot.musicautobot.multitask_transformer.learner import (
    mask_predict_from_midi,
    multitask_model_learner,
    s2s_predict_from_midi,
)
from musicbot.musicautobot.music_transformer.dataloader import MusicDataBunch
from musicbot.musicautobot.music_transformer.transform import MusicItem, SEQType

data_path = pathlib.Path("/home/cunning/studying/diploma/musicData/")
data = MusicDataBunch.empty(data_path)
vocab = data.vocab
pretrained_path = pathlib.Path(
    "/home/cunning/studying/diploma/musicautobot/data/numpy/models/MultitaskSmall.pth"
)
config = multitask_config()
learn = multitask_model_learner(data, config=config, pretrained_path=pretrained_path)


def handle_uploaded_file(f):
    midi = f.read()
    n_words = 120
    temperatures = 1.0, 1.0
    # full = s2s_predict_from_midi(learn, midi=midi, n_words=n_words, temperatures=temperatures, seed_len=8,
    #  pred_melody=True, use_memory=True, top_k=10, top_p=0.2).chords
    item = MusicItem.from_file(midi, vocab=vocab)
    empty_item = MusicItem.empty(vocab, seq_type=SEQType.Chords)
    prediction = learn.predict_s2s(
        input_item=item,
        target_item=empty_item,
        n_words=n_words,
        temperatures=temperatures,
    )
    # combined = MultitrackItem(item, empty_chords)
    # combined.
    file_location = data_path / "result.mid"
    pathlib.Path(prediction.to_stream(bpm=120).write("midi", file_location))


@api_view(["POST"])
def test(request):
    print("FILES::")
    print(request.FILES)
    print("POST::")
    print(request.POST)
    
    midi_file = request.FILES["file"]
    # operation_code=request.POST['operation_code']
    handle_uploaded_file(midi_file)
    with open(data_path / "result.mid", "rb") as f:
        file_data = f.read()
    response = HttpResponse(file_data, content_type="audio/midi")
    response["Content-Disposition"] = 'attachment; filename="song.mid"'
    return response


@api_view(["GET", "POST"])
def upload_file(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES["file"])

            with open(data_path / "result.mid", "rb") as f:
                file_data = f.read()
            response = HttpResponse(file_data, content_type="audio/midi")
            response["Content-Disposition"] = 'attachment; filename="song.mid"'
            return response

    else:
        form = UploadFileForm()
    return render(request, "upload.html", {"form": form})


@api_view(["GET"])
def getAccords(request):
    return render(request, "test.html")
    request.files
    return HttpResponse("on air!")


@api_view(["GET", "POST"])
def getAudio(request):
    file_location = "/home/cunning/testmusic.mid"
    empty_melody = MusicItem.empty(vocab)
    # predict_nw, full = learn.predict_nw(empty_melody, n_words = 100)
    pitch_temp = 0.8  # randomness of melody
    tempo_temp = 0.8  # randomness or rhythm
    top_k = 40
    predict_nw, full= learn.predict_nw(
        empty_melody,
        temperatures=(pitch_temp, tempo_temp),
        top_k=top_k,
        top_p=0.5,
        n_words=200,
    )   
    pathlib.Path(predict_nw.to_stream(bpm=120).write("midi", file_location))
    try:
        with open(file_location, "rb") as f:
            file_data = f.read()

        # sending response
        response = HttpResponse(file_data, content_type="audio/midi")
        response["Content-Disposition"] = 'attachment; filename="song.mid, song.mid"'

    except IOError:
        # handle file not exist case here
        response = HttpResponseNotFound("<h1>File not exist</h1>")

    return response
    # return JsonResponse(dict)


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


# Create your views here.
