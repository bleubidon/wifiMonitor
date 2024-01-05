<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>&#65279;</title>
  <style>
    table, th, td {
      border: 1px solid black;
    }
  </style>
  <script>
    function get_json() {
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.onreadystatechange = function() {
          if (this.readyState == 4 && this.status == 200) {
            document.body.innerHTML = this.responseText;
          }
        };
        xmlhttp.open("POST", "render.php", true);
        xmlhttp.send();
      }
  </script>
</head>

<body>
  <script>setInterval(get_json, 1000)</script>
</body>
</html>
