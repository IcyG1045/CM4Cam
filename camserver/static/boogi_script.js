// Get Time

function getTimeNow() {
         var CurrentTime = new Date(),
             h = (CurrentTime.getHours()<10?'0':'') + CurrentTime.getHours();
             m = (CurrentTime.getMinutes()<10?'0':'') + CurrentTime.getMinutes();
             s = (CurrentTime.getSeconds()<10?'0':'') + CurrentTime.getSeconds();

        var rntime = h + ":" + m +":" + s;

        return rntime;

}



