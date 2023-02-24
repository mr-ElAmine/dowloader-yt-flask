from flask import Flask, request, render_template, redirect, url_for, session, send_file, Blueprint
import pytube, pytube.exceptions
from flask_wtf import FlaskForm
from wtforms import StringField, validators
from io import BytesIO

views = Blueprint('views', __name__)

class DownloadForm(FlaskForm):
    link = StringField('link', validators=[validators.DataRequired()])

@views.route('/', methods=['GET', 'POST'])
def index():
    error = None
    form = DownloadForm(request.form)

    if request.method == 'POST' and form.validate_on_submit():

        session['link'] = form.link.data

        try:

            url = pytube.YouTube(session['link'])
            mp4 = url.streams.filter(file_extension='mp4')
            mp3 = url.streams.filter(only_audio=True, file_extension='mp3')
            if mp4.first() or mp3.first():
                if not url.check_availability():
                    return render_template('filtered.html', name_page='Filtered', error=error, url=url, mp3=len(mp3), mp4=len(mp4))
                else:
                    error = 'The video you are trying to download is not available'
            else: 
                error = 'This video cannot be downloaded in the formats offered by on service'

        except pytube.exceptions.VideoUnavailable as e:
            error = 'The video you are trying to download is not available'
        except pytube.exceptions.RegexMatchError as e:
            error = 'Invalid URL, please check the link and try again'
        except Exception as e:
            error = f'An error occurred, please check the link and try again. {e}'

    return render_template('index.html', form=form, error=error, name_page ='Home')


@views.route('/filtered', methods=['GET', 'POST'])
def filtered():
    if request.method == 'POST':
        if not request.form.get('submit_button') == "Go back":

            link = session.get('link')
            url = pytube.YouTube(link)
            
            mp3 = session.get('mp3')
            mp4 = session.get('mp4')

            session['file_format'] = request.form.get('file_format')

            return render_template('download.html', file_format=request.form.get('file_format'), url=url, name_page ='Download')

        else:

            return redirect(url_for('index'))

    return render_template('index.html', error="An error occured", name_page ='Home')

@views.route('/download', methods=['GET', 'POST'])
def download_yt():  
    link = session.get('link')
    url = pytube.YouTube(link)
    file_format = session.get('file_format')

    if request.method == 'POST' and request.form.get('submit_button'):
        if not request.form.get('submit_button') == "Home":

            if file_format == 'mp3':
                audio_quality = request.form.get('audio_quality')
                video = url.streams.filter(only_audio=True, file_extension='mp3', abr=audio_quality).first()
            else:
                video_resolution = request.form.get('video_resolution')
                video = url.streams.filter(file_extension='mp4', res=video_resolution).first()

            filename = f'{url.title}.{file_format}'
            buffer = BytesIO()

            video.stream_to_buffer(buffer)
            buffer.seek(0)

            return send_file(buffer ,as_attachment=True, download_name=filename)
        
        else:

            return redirect(url_for('index'))

    return render_template('download.html', file_format=file_format, url=url, name_page ='Download')