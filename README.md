# Song-Fingerprint

This listens for a song and predicts what song is being played based on information about the local peaks of the ofrier transform of the input data.

Alexa Skill:
  name: SongFP

  Invoaction phrase: fingerprint
  
  Intent Schematic:
  ```{
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
}```


Sample Utterances:
```RecordSong Record for {five | length} seconds
RecordSong Record for {ten | length} seconds
RecordSong Record for {twenty | length} seconds
RecordSong Record for {fourty | length} seconds
RecordSong {five | length} seconds
RecordSong {ten | length} seconds
RecordSong {twenty | length} seconds
RecordSong {fourty | length} seconds```
