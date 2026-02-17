from django.shortcuts import render
from .forms import UploadFileForm

def home_page(request):
    return render(request, 'main/index.html')


def comparison(request):
    form = UploadFileForm()

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)


        all_files = []
        for key in request.FILES.keys():
            all_files.extend(request.FILES.getlist(key))

        if not all_files:
            return render(request, 'main/comparison.html', {
                'form': form,
                'message': "Error: No files received. Please try again.",
                'msg_type': 'danger'
            })

        new_form = UploadFileForm()

        return render(request, 'main/comparison.html', {
            'form': new_form,
            'message': f"Success! Uploaded {len(all_files)} resumes. Ready to analyze.",
            'msg_type': 'success'
        })

    return render(request, 'main/comparison.html', {'form': form})


def about(request):
    return render(request, 'main/about.html')

def contact(request):
    return render(request, 'main/contact.html')



