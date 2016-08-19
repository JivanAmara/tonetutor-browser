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
    rb.style.backgroundColor = 'f77';
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
        
        example_audio = document.getElementById(example_audio_id);
        example_audio.src = data.url;
        example_audio.load();
        prompt = document.getElementById(prompt_id);
        prompt.innerHTML = data.display;
    });
}

function checkRecording(e) {
    /* Sends the user's attempt to the server for analysis & displays the appropriate image
     *  based on success/failure/indeterminable.
     */
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
    el.src = URL.createObjectURL(e.data);
    var fd = new FormData();
    // Get extension
    typePieces = e.data.type.split('/');
    ext = typePieces[typePieces.length - 1];
    fd.append('attempt', e.data);
    fd.append('csrfmiddlewaretoken', csrfToken);
    fd.append('extension', ext);
    fd.append('expected_sound', syllable.sound);
    fd.append('expected_tone', syllable.tone);

    $.ajax({
        type: 'POST',
        url: checkSyllableUrl,
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
