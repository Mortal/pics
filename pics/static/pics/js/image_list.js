// vim: set sw=2 et:
///////////////////////////////////////////////////////////////////////////////
// The following is from
// https://docs.djangoproject.com/en/dev/ref/contrib/csrf/#ajax

function getCookie(name) {
  if (!document.cookie || document.cookie == '') return null;
  var cookies = document.cookie.split(';');
  for (var i = 0; i < cookies.length; i++) {
    var cookie = jQuery.trim(cookies[i]);
    // Does this cookie string begin with the name we want?
    if (cookie.substring(0, name.length + 1) == (name + '=')) {
      return decodeURIComponent(cookie.substring(name.length + 1));
    }
  }
  return null;
}

var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
  // these HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function sameOrigin(url) {
  // test that a given url is a same-origin URL
  // url could be relative or scheme relative or absolute
  var host = document.location.host; // host + port
  var protocol = document.location.protocol;
  var sr_origin = '//' + host;
  var origin = protocol + sr_origin;
  // Allow absolute or scheme relative URLs to same origin
  return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
    (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
    // or any other URL that isn't scheme relative or absolute i.e relative.
    !(/^(\/\/|http:|https:).*/.test(url));
}

$.ajaxSetup({
  beforeSend: function(xhr, settings) {
    if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
      // Send the token to same-origin, relative URLs only.
      // Send the token only if the method warrants CSRF protection
      // Using the CSRFToken value acquired earlier
      xhr.setRequestHeader("X-CSRFToken", csrftoken);
    }
  }
});

// end snippet from Django
///////////////////////////////////////////////////////////////////////////////

function Image(element) {
  if (element == null) {
    var img = document.createElement('img');
    element = document.createElement('li');
    element.appendChild(img);
  }
  this.element = element;
  this.imgElement = element.querySelector('img');
}

function get_data_attribute(attribute) {
  return function get_attribute() {
    if (this.element.hasAttribute('data-'+attribute))
      return this.element.getAttribute('data-'+attribute);
    else
      return null;
  };
}

function set_data_attribute(attribute) {
  return function set_attribute(value) {
    if (value == null)
      this.element.removeAttribute('data-'+attribute);
    else
      this.element.setAttribute('data-'+attribute, value);
  };
}

Image.prototype.get_pk = get_data_attribute('pk');
Image.prototype.set_pk = set_data_attribute('pk');

Image.prototype.get_filename = get_data_attribute('filename');
Image.prototype.set_filename = set_data_attribute('filename');

Image.prototype.get_uploadindex = get_data_attribute('uploadindex');
Image.prototype.set_uploadindex = set_data_attribute('uploadindex');

function get_images() {
  var imagegrid = document.getElementsByClassName('imagegrid')[0];
  var result = [];
  for (var e = imagegrid.firstChild; e != null; e = e.nextSibling) {
    if (e.nodeType != 1) continue;
    result.push(new Image(e));
  }
  return result;
}

function post_positions() {
  var images = get_images();
  var pks = [];
  for (var i = 0, l = images.length; i < l; ++i) {
    var e = images[i];
    var pk = e.get_pk();
    if (pk != null) pks.push(pk);
  }
  $.post('reorder/', {'images': pks.join(',')});
}

$(function () {
  $(".imagegrid").sortable({
    'placeholder': 'placeholder',
    'stop': function (event, ui) { post_positions(); }
  });
});

/*
function PriorityList(n) {
  this._n = n;
  this._values = new Array(n);
  this._topprio = n;
}
PriorityList.prototype.set = function PriorityList_set(priority, value) {
  this._values[priority] = value;
  this._topprio = Math.min(this._topprio, priority);
  while (this._topprio < this._n && this._values[this._topprio] == null) {
    this._topprio++;
  }
};
PriorityList.prototype.top = function PriorityList_top() {
  if (this._topprio == this._n) return null;
  else return this._values[this._topprio];
};

var currentFocus = new PriorityList(2);
$('.imagegrid li').on('mouseover', function () {
  currentFocus.set(0, this);
});
$(window).on('keypress', function (ev) {
  if (ev.charCode == 'j'.charCodeAt(0)) {
    //currentFocus.set(
  }
});
*/

function Queue() {
  this.q = [];
  this.head = 0;
}

Queue.prototype.empty = function Queue_empty() { return this.head == this.q.length; };
Queue.prototype.top = function Queue_top() { return this.empty() ? null : this.q[this.head]; };
Queue.prototype.push = function Queue_push(v) { this.q.push(v); };
Queue.prototype.pop = function Queue_pop() {
  if (this.empty()) return;
  if (++this.head == this.q.length) {
    this.head = 0;
    this.q = [];
  }
};

function is_image(file) {
  return file.type.match(/^image\//);
}

function make_image_placeholder(file) {
  var img = new Image();
  document.getElementsByClassName('imagegrid')[0].appendChild(img.element);
  img.set_filename(file.name);
  return img;
}

var readingQueue = new Queue();
var reader = new FileReader();
var isReading = false;
reader.onload = function(e) {
  var img = readingQueue.top().img.imgElement;
  img.src = reader.result;
  readingQueue.pop();
  isReading = false;
  read_next_image();
};

function read_next_image() {
  if (isReading || readingQueue.empty()) return;
  isReading = true;
  var file = readingQueue.top().file;
  reader.readAsDataURL(file);
}

function read_image_into(file, img) {
  readingQueue.push({file: file, img: img});
  read_next_image();
}

var uploadtasks = [];
var isUploading = false;

function get_next_upload_task_index() {
  var images = get_images();
  var uploadIndex = null;
  for (var i = 0, l = images.length; i < l; ++i) {
    var img = images[i];
    if (img.get_uploadindex() == null) continue;
    uploadIndex = img.get_uploadindex();
    break;
  }
  return uploadIndex;
}

function update_upload_progress() {
  var images = get_images();
  var remaining = 0;
  for (var i = 0, l = images.length; i < l; ++i) {
    var img = images[i];
    if (img.get_uploadindex() != null) ++remaining;
  }
  var state;
  if (remaining == 0) {
    state = 'All images have been uploaded';
  } else if (remaining == 1) {
    state = 'Uploading: 1 image remaining';
  } else {
    state = 'Uploading: '+remaining+' images remaining';
  }
  document.getElementById('upload_progress').textContent = state;
}

function upload_next() {
  if (isUploading) return;
  isUploading = true;

  update_upload_progress();
  var uploadIndex = get_next_upload_task_index();
  if (uploadIndex == null) return;
  var task = uploadtasks[uploadIndex];
  var fd = new FormData();
  fd.append('image', task.file, task.file.name);
  var jqXHR = $.ajax({
    url: 'upload/?ajax=1',
    data: fd,
    processData: false,
    contentType: false,
    type: 'POST',
    dataType: 'json',
    xhrFields: {
      onprogress: function (e) {
        if (e.lengthComputable) {
          task.progress.set(e.loaded, e.total);
        }
      }
    },
    success: function (data) {
      task.done(data);
      isUploading = false;
      upload_next();
    },
    error: function (jqXHR, textStatus, errorThrown) {
      task.set_failed_status(textStatus);
      isUploading = false;
      upload_next();
    }
  });
  /*
  var xhr = new XMLHttpRequest();
  xhr.open('POST', 'upload/', true);
  xhr.onreadystatechange = function () {
    if (xhr.readyState == 4) {
      if (xhr.status == 200) {
        var data = JSON.parse(xhr.responseText);
        task.done(data);
      } else {
        task.set_failed_status(xhr.status);
      }
      uploadtasks[uploadIndex] = null;
      upload_next();
    }
  };
  xhr.upload.addEventListener('progress', function (e) {
    if (!e.lengthComputable) return;
    var progress = e.loaded / e.total;
    task.set_progress(progress);
  }, false);
  xhr.send(fd);
  */
}

function ProgressElement() {
  var el = this.element = document.createElement('progress');
}

ProgressElement.prototype.set = function ProgressElement_set(loaded, total) {
  this.element.max = total;
  this.element.value = loaded;
};

function UploadTask(file, image) {
  this.file = file;
  this.image = image;

  this.progress = new ProgressElement();

  this.progressOverlay = document.createElement('div');
  this.progressOverlay.className = 'progressoverlay';
  this.progressOverlay.appendChild(this.progress.element);
  this.image.element.appendChild(this.progressOverlay);
}

UploadTask.prototype.set_failed_status = function UploadTask_set_failed_status(status) {
  this.progressOverlay.textContent = "Failed: "+status;
  this.remove_from_upload_queue();
};

UploadTask.prototype.done = function UploadTask_done(data) {
  if (data.length == 0) {
    console.log("UploadTask_done: no data");
    return;
  }
  if (data.length > 1) {
    console.log("UploadTask_done: too much data");
  }
  var imageData = data[0];
  var pk = imageData['pk'];
  var filename = imageData['filename'];
  var originalFilename = imageData['original_filename'];
  var thumbnail = imageData['thumbnail'];
  if (originalFilename != this.file.name) {
    console.log("UploadTask_done: wrong original filename");
  }
  this.image.set_pk(pk);
  this.image.element.removeChild(this.progressOverlay);
  this.image.imgElement.src = thumbnail;
  this.progress = null;
  this.remove_from_upload_queue();
};

UploadTask.prototype.remove_from_upload_queue = function UploadTask_remove() {
  var uploadIndex = this.image.get_uploadindex();
  if (uploadIndex == null) {
    console.log("UploadTask.remove_from_upload_queue: not in queue?");
    return;
  }
  this.image.set_uploadindex(null);
  uploadtasks[uploadIndex] = null;
};

function upload_image(file, image) {
  var task = new UploadTask(file, image);
  image.set_uploadindex(uploadtasks.length);
  uploadtasks.push(task);
  upload_next();
}

function handle_files(filesField) {
  var files = filesField.files;
  for (var i = 0, l = files.length; i < l; ++i) {
    var file = files[i];
    if (!is_image(file)) continue;
    var img = make_image_placeholder(file);
    read_image_into(file, img);
    upload_image(file, img);
  }
  filesField.form.reset();
}
