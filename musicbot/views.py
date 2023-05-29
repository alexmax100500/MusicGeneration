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


def handle_uploaded_file(f, pitch_temp, tempo_temp, n_words, operation_code):
    midi = f.read()
    temperatures = pitch_temp, tempo_temp
    # full = s2s_predict_from_midi(learn, midi=midi, n_words=n_words, temperatures=temperatures, seed_len=8,
    #  pred_melody=True, use_memory=True, top_k=10, top_p=0.2).chords
    item = MusicItem.from_file(midi, vocab=vocab)
    if operation_code == 0:
        seq_type= SEQType.Chords
    else:
        seq_type= SEQType.Melody
    empty_item = MusicItem.empty(vocab, seq_type=seq_type)
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
    
    pitch_temp = float(request.POST['pitch_temp'])
    print(pitch_temp)
    tempo_temp = float(request.POST['tempo_temp'])
    print(tempo_temp)
    n_words = int(request.POST['n_words'])
    print(n_words)
    midi_file = request.FILES["file"]
    operation_code=int(request.POST['operation_code'])
    handle_uploaded_file(midi_file, pitch_temp=pitch_temp, tempo_temp=tempo_temp, n_words=n_words, operation_code=operation_code)
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
    pitch_temp = float(request.POST['pitch_temp'])
    tempo_temp = float(request.POST['tempo_temp'])
    n_words = int(request.POST['n_words'])
    file_location = "/home/cunning/testmusic.mid"
    empty_melody = MusicItem.empty(vocab)
    # predict_nw, full = learn.predict_nw(empty_melody, n_words = 100)
    top_k = 40
    predict_nw, full= learn.predict_nw(
        empty_melody,
        temperatures=(pitch_temp, tempo_temp),
        top_k=top_k,
        top_p=0.5,
        n_words=n_words,
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
