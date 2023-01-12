var testdataBucketName = "codebreaker-testdata";
var bucketRegion = "ap-southeast-1";
var accessKeyId = "ASIAVE5FZNLWAL5YDPRZ"
var secretAccessKey = "kdODw9Llh5YhxeJ0Q2k/wG5w60Sx5CO+S5ajo4or";
var sessionToken = "FwoGZXIvYXdzEF8aDJ32VspeVpRaNVwBKyKrARdkcoN+pvywEyMhuWliEpaOOWf2yAacsZZzcmTsQBcAHJK7Zkup0FXNofiX5xSTwOcsEIWxuR/r2dLYn7451YqCgX6Rc2pclCQIVdwI0/YNSQtl378l8ErXLdMBAgdB1I79bfOl9FY4C8DXNxOsSPkVDXw+Uvu+enBaODVac4BOk7SyHOFo+mm1vxsfOog5nw8M8FXIn8vmrWW3QaduOFolvWqzS/P9VzSUBCiK6/qdBjItOmoY7Gl36g3BgZaIk3K4ljVFGJ1ZgJPnD7tvet6KseBOzlpopJJXwsEnaVfq"
var problemName = "helloworld"

AWS.config = new AWS.Config();
AWS.config.accessKeyId = accessKeyId;
AWS.config.secretAccessKey = secretAccessKey;
AWS.config.sessionToken = sessionToken;
AWS.config.region = bucketRegion;

var i = 0;
function move() {
  if (i == 0) {
    i = 1;
    var elem = document.getElementById("myBar");
    var width = 1;
    var id = setInterval(frame, 10);
    function frame() {
      if (width >= 100) {
        clearInterval(id);
        i = 0;
      } else {
        width++;
        elem.style.width = width + "%";
      }
    }
  }
}

console.log(AWS.config)

var s3 = new AWS.S3({
  apiVersion: "2006-03-01",
  config: AWS.config
});

var keys = {{stsKeys}}
console.log(keys)

upload = () => {
  var keys = {{stsKeys}}
  console.log(keys)
	$('#myProgress').show();

  var files = document.getElementById("uploadFiles").files;

  if (!files.length) {
    return alert("Please choose a file to upload first.");
  }

  for (var i = 0; i < files.length; i++){
  	var file = files[i];
  	var fileName = file.name;
  	var Key =  problemName + "/" + fileName

  	// Use S3 ManagedUpload class as it supports multipart uploads
	  var upload = new AWS.S3.ManagedUpload({
	    params: {
	      Bucket: testdataBucketName,
	      Key: Key,
	      Body: file
	    }
	  });

	  var promise = upload.promise();

	  promise.then(
    function(data) {
    	move()
      console.log(data)
    },
    function(err) {
    	console.log(err)
    }
  );
  }
}