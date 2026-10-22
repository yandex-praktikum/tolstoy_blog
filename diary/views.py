from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from .models import Entry


@login_required
def entry_list(request):
    return render(request, 'diary/entries.html', {'entries': Entry.objects.all()})


@login_required
def entry_detail(request, pk):
    return render(request, 'diary/entry.html', {'entry': get_object_or_404(Entry, pk=pk)})


def public_page(request, page_path):
    import json
    from pathlib import Path
    from django.http import Http404, HttpResponse

    directory = Path(__file__).resolve().parent
    manifest = json.loads((directory / 'public_pages.json').read_text(encoding='utf-8'))
    key = '/' + page_path
    page = request.GET.get('page', '1')
    if page != '1':
        key += '?page=' + page
    filename = manifest.get(key)
    if filename is None:
        raise Http404('Страница учебного блога не найдена')
    if filename.endswith('.css'):
        stylesheet = directory / 'static' / 'diary' / filename
        return HttpResponse(stylesheet.read_text(encoding='utf-8'), content_type='text/css')
    return render(request, 'diary/public/' + filename)


@login_required
def diary_page(request, page_path):
    import json
    from pathlib import Path
    from django.http import Http404

    directory = Path(__file__).resolve().parent
    manifest = json.loads((directory / 'private_pages.json').read_text(encoding='utf-8'))
    key = '/' + page_path
    page = request.GET.get('page', '1')
    if page != '1':
        key += '?page=' + page
    filename = manifest.get(key)
    if filename is None:
        raise Http404('Страница учебного блога не найдена')
    return render(request, 'diary/private/' + filename)
