# Song-Fingerprint

## Returns Name and percent accuracy of song - 

This listens to a song and returns the the accuracy (in percentage) of the song that has the most matches in local peaks, the song that it returns is always in the database.

for example - "I am 81% confident that this song is Don't Stop Believeing"

## Installation Instuctions:

2) Clone repository into desired file 

3) Run setup.py files to run face recognition use following command:

      ```python sfp_setup.py develop```
      
4) Use the command to start the face recognition package after running the setup.py file (use the following command): 
     
     ```import song_fingerprint as fp```

Alexa Skill:
  name: SongFP

  Invoaction phrase: fingerprint
  
  Intent Schematic:
  ```
{
  "intents": [
    {
      "slots": [
        {
          "name": "length",
          "type": "NUMBER"
        }
      ],
      "intent": "RecordSong"
    }
  ]
}
```
Sample Utterances:

```
RecordSong Record for {five | length} seconds
RecordSong Record for {ten | length} seconds
RecordSong Record for {twenty | length} seconds
RecordSong Record for {fourty | length} seconds
RecordSong {five | length} seconds
RecordSong {ten | length} seconds
RecordSong {twenty | length} seconds
RecordSong {fourty | length} seconds```
