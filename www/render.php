<?php
$html_array = "<table>";
$wifi_data_json = json_decode(file_get_contents("../wifiData.json"), true)["stations"];
$wifi_data_json_stations = array_keys($wifi_data_json);

foreach ($wifi_data_json_stations as $station) {
    $html_array .= "<tr>";

    $html_array .= "<td>";
    $html_array .= $station;
    $html_array .= "</td>";
    foreach($wifi_data_json[$station] as $event_date) {
        $html_array .= "<td>";
        $html_array .= $event_date;
        $html_array .= "</td>";
    }
    $html_array .= "</tr>";
}
$html_array .= "</table>";

echo $html_array;
