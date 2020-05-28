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
    if (count($episodes_to_send) != 0) {
        $episode = $episodes_to_send[0];
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
        $result['file_type'] = $method;
        if ($result['file_type'] == 'photo') {
            $result['file_size'] = $botAPI_file[$method][0]['file_size'];
            if (isset($botAPI_file[$method][0]['file_name'])) {
                $result['file_name'] = $botAPI_file[$method][0]['file_name'];
                $result['file_id'] = $botAPI_file[$method][0]['file_id'];
            }
        } else {
            if (isset($botAPI_file[$method]['file_name'])) {
                $result['file_name'] = $botAPI_file[$method]['file_name'];
            }
            if (isset($botAPI_file[$method]['file_size'])) {
                $result['file_size'] = $botAPI_file[$method]['file_size'];
            }
            if (isset($botAPI_file[$method]['mime_type'])) {
                $result['mime_type'] = $botAPI_file[$method]['mime_type'];
            }
            $result['file_id'] = $botAPI_file[$method]['file_id'];
        }
        if (!isset($result['mime_type'])) {
            $result['mime_type'] = 'application/octet-stream';
        }
        if (!isset($result['file_name'])) {
            $result['file_name'] = $result['file_id'].($method === 'sticker' ? '.webp' : '');
        }

        $episode_file_id = $result['file_id'];

        $fp = fopen($episode_file_id_path, "wb");
        fwrite($fp, $episode_file_id);
        fclose($fp);
    }
    sleep(1);
}