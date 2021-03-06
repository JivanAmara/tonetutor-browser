function bestAudioMimeType() {
    // Mime types in order of preference
    var mime_types = ['audio/webm', 'audio/ogg'];
    var preferred = null;
    for (var i = 0; i < mime_types.length; i++) {
        if ( MediaRecorder.isTypeSupported(mime_types[i]) ) {
            preferred = mime_types[i];
            break;
        }
    }
    return preferred;
}

function startRecording(recorder, recorder_state) {
    /* Starts recording, updates the record button to indicate recording, and hides the
     * user's previous attempt audio controls.
     * 
     * recorder - MediaRecorder instance
     */
    recorder.start();
    recorder_state.recording = true;
    $('#attempt').hide(0);
    var rb = document.getElementById('record_button');
    rb.style.backgroundColor = '#f77';
}

function stopRecording(recorder, recorder_state) {
    /* Stops recording, updates the record button to indicate recording, and hides the
     * user's previous attempt audio controls.
     */
    recorder.stop();
    recorder_state.recording = false;
    $('#attempt').show(0);
    var rb = document.getElementById('record_button');
    rb.style.backgroundColor = '';
}

function getSyllable(example_audio_id, prompt_id, syllable) {
    /* Collects a new syllable, updates the example audio, prompt, and sets the
        tone attribute of object 'syllable'.
    */
    $.ajax({
        type: 'GET',
        url: getSyllableUrl,
        dataType: 'json'
    }).done(function(data){
        syllable.tone = data.tone;
        syllable.sound = data.sound;
        syllable.display = data.display;
        syllable.url = data.url;
        syllable.hanzi = data.hanzi;

        example_audio = document.getElementById(example_audio_id);
        example_audio.src = data.url;
        example_audio.load();
        prompt = document.getElementById(prompt_id);
        var display_text = data.display;
        var hanzi_list = '';
        for (var i = 0; i < syllable.hanzi.length; i++) {
            hanzi_list = hanzi_list + syllable.hanzi[i][0];
            if (i < syllable.hanzi.length - 1) {
                hanzi_list = hanzi_list + ', '
            }
        }
        display_text = display_text + ' (' + hanzi_list + ')';
        prompt.innerHTML = display_text;
    });
}

function checkRecording(e) {
    /* Sends the user's attempt to the server for analysis & displays the appropriate image
     *  based on success/failure/indeterminable.
     */
    /* If there's data, save it */
    if (e.data.size > 0) {
        recorder_state.audio_chunks.push(e.data);
    }

    /* If we're still recording, don't send the data to the server yet. */
    if (recorder_state.recording == true) {
        return;
    }

    /* Ignore sending the recording if it ended by the user clicking 'next'. */
    if (next_clicked) {
        next_clicked = false;
        return;
    }
    
    // show the spinner in case of a long api request.
    $('#result_section img').hide(0);
    $('#spinner').show(0);

    // e.data contains the audio data! let's associate it to an <audio> element
    var el = document.getElementById('attempt_audio');
    //document.querySelector('audio');
    var audio_data = new Blob(recorder_state.audio_chunks);
    recorder_state.audio_chunks = [];
    el.src = URL.createObjectURL(audio_data);
    var fd = new FormData();
    
    // Make extension from mime type
    var ext = null;
    if (recorder_state.mimeType == 'audio/webm') {
        ext = 'webm';
    }
    else if (recorder_state.mimeType == 'audio/ogg') {
        ext = 'ogg';
    }
    
    fd.append('attempt', audio_data);
    fd.append('csrfmiddlewaretoken', csrfToken);
    fd.append('extension', ext);
    fd.append('expected_sound', syllable.sound);
    fd.append('expected_tone', syllable.tone);

    $.ajax({
        type: 'POST',
        url: checkSyllableUrl,
        headers: {'Authorization': 'Token ' + authToken},
        data: fd,
        processData: false,
        contentType: false,
        dataType: 'json'
    }).done(function(data) {
        console.log(data);
        if (data.status) {
            $('#result_section img').hide(0);
            
            if (data.tone == null) {
                $('#question').fadeIn(500);
            }
            else if (data.tone == syllable.tone) {
                $('#success').fadeIn(500);                        
            }
            else if (data.tone != syllable.tone) {
                $('#failure').fadeIn(500);
            }
        }
    });
}
