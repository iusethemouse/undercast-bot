<?php

if (!file_exists('madeline.php')) {
    copy('https://phar.madelineproto.xyz/madeline.php', 'madeline.php');
}
include 'madeline.php';


$settings['app_info']['api_id'] = "your_Telegram_API_ID";
$settings['app_info']['api_hash'] = "your_Telegram_API_hash";

$MadelineProto = new \danog\MadelineProto\API('session.madeline', $settings);
$MadelineProto->start();


while (TRUE) {
    $path = "episodes_to_send/*.mp3";
    $episodes_to_send = glob($path);
    foreach ($episodes_to_send as $episode) {
        // the '- 4' below is to remove the '.mp3' extension from the end of the path (sloppy)
        $episode_data = substr($episode, 0, strlen($episode) - 4) . "_data.txt";
        $episode_file_id_path = substr($episode, 0, strlen($episode) - 4) . ".txt";

        $data_file = fopen($episode_data, 'r');
        $data = fgets($data_file);
        fclose($data_file);
        $data = explode("::", $data);
        $title = $data[0];
        $artist = $data[1];
        $thumb_id = $data[2];

        $sentMessageAudio = $MadelineProto->messages->uploadMedia( ['peer' => 'me',
                                                                   'media' => ['_' => 'inputMediaUploadedDocument', 
                                                                               'file' => $episode,
                                                                               'attributes' => [['_' => 'documentAttributeAudio', 
                                                                                                 'voice' => false,
                                                                                                 'title' => $title,
                                                                                                 'performer' => $artist]
                                                                                                ]
                                                                                ],
                                                                    'thumb' => $thumb_id
                                                                    ] );

        unlink($episode);
        unlink($episode_data);

        $botAPI_file = $MadelineProto->MTProtoToBotAPI($sentMessageAudio);

        foreach (['audio', 'document', 'photo', 'sticker', 'video', 'voice', 'video_note'] as $type) {
            if (isset($botAPI_file[$type]) && is_array($botAPI_file[$type])) {
                $method = $type;
            }
        }
        
        $episode_file_id = $botAPI_file[$method]['file_id'];

        $fp = fopen($episode_file_id_path, "wb");
        fwrite($fp, $episode_file_id);
        fclose($fp);
    }
    sleep(1);
}