<template>
  <div id="dboard">
    <canvas ref="board"></canvas>
    <div class="other">
      <div class="paleta" v-if="eReady">
        <button class="colButton" style="background-color: red;" v-on:click="switchColor('Red')"></button>
        <button class="colButton" style="background-color: green;" v-on:click="switchColor('Green')"></button>
        <button class="colButton" style="background-color: blue;" v-on:click="switchColor('Blue')"></button>
        <button class="colButton" style="background-color: black;" v-on:click="switchColor('Black')"></button>
        <button class="colButton" style="background-color: yellow;" v-on:click="switchColor('Yellow')"></button>
        <button class="colButton" v-on:click="clearBoard">Očisti tablu</button>
      </div>
      <div id="leaderboard">
        <ul id="leaderBox">
          <li class="playerBox" v-for="item in players" :key="item[0]">
            <span class="ime">{{ item[0] }}: </span>
            <span class="poeni">{{ item[1] }}</span>
          </li>
        </ul>
        <button v-if="notReady" v-on:click="playerReady()" id="readyButton">Spreman!</button>
      </div>
      <div id="chat">
         <ul id="chatBox">
              <li class="message" v-for="item in messageList" :key="item.id">
                  <div class="messageBox">
                      <span class="sender">{{ item.cont[0] }}: </span>
                      <span class="messageText">{{ item.cont[1] }}</span>
                  </div>
              </li>
          </ul>
          <div id="inputAndSend">
            <input type="text" id="messageInput" v-model="tekst">
            <button id="sendButton" v-on:click="sendMessage()">Pošalji</button>
          </div>
      </div>
    </div>
    <span id="misc">{{usr}}
      <span v-if="eReady">Nacrtaj: {{topic}} Vreme: {{this.time}}</span>
    </span>
  </div>
</template>

<script>
import io from "socket.io-client"

export default {
  name: "DrawingBoard",
  props: {
    usr: String,
    code: String    
  },
  data() {
    return {
      socket: null,
      canvas: null,
      ctx: null,
      painting: false,
      tekst: '',
      messageList: [],
      msgCount: 0,
      players: [],
      notReady: true,
      eReady: false,
      topic: '',
      time: 30,
      intervalid1: null,
      cetvrta: 0
    };
  },
  created() {
    this.socket = io('http://0.0.0.0')
  },
  mounted() {
    this.canvas = this.$refs.board;

    this.canvas.width = 0.5 * window.innerWidth;
    this.canvas.height = 0.7 * window.innerHeight;

    this.ctx = this.canvas.getContext('2d')
    this.ctx.lineWidth = 10;

    this.socket.on('coordinates', data => this.drawFrom(data))
    this.socket.on('begin', data => {
      this.xx = data.x;
      this.xy = data.y;
      this.socket.emit('beginconfirm')
    })
    this.socket.on('switchColor', data => {
      this.ctx.strokeStyle = data;
    })
    this.socket.on('clear', () => {
      this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height)
    })
    this.socket.on('sendMessage', (data) => {
      this.messageList.push({
        id: this.msgCount,
        cont: data
      })
      this.msgCount += 1
    })
    this.socket.on('newPlayer', (data) => {      
      this.players = data
    })
    this.socket.on('eReady', (data) => {
      this.eReady = true
      this.topic = data
      this.intervalid1 = setInterval(() => {
        this.time -= 1;
        if (this.time <= 0)
          this.timeUp();
      }, 1000)
    })
    this.socket.on('clearXs', () => {
      this.ctx.beginPath();
    })
    this.socket.on('clearChat', () => {
      this.messageList = []
    })
    this.socket.emit('addMe', [this.$props.usr, this.$props.code])

    this.canvas.addEventListener('mousedown', this.mousedown);
    this.canvas.addEventListener('mouseup', this.mouseup);
    this.canvas.addEventListener('mousemove', this.draw);
  },
  methods: {
    switchColor(color) {
      this.ctx.strokeStyle = color;
      this.socket.emit('switchColor', color)
    },
    clearBoard() {
      this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height)
      this.socket.emit('clear')
    },
    mousedown(e) {
      if (this.eReady) {
      this.painting = true;
      this.socket.emit('begin', {x:e.clientX, y:e.clientY})
      this.draw(e);
      }
    },
    mouseup() {
      this.painting = false;
      this.ctx.beginPath();                 
      this.socket.emit('end')
    },
    draw(e) {
      if (!this.painting) return;
      this.ctx.lineWidth = 10;
      this.ctx.lineCap = "round";
      if (this.cetvrta % 2 == 0) {this.socket.emit('coordinates', {x:e.clientX, y:e.clientY})}
      this.cetvrta += 1   

      this.ctx.lineTo(e.clientX, e.clientY)
      this.ctx.stroke();
      this.ctx.beginPath();
      this.ctx.moveTo(e.clientX, e.clientY)
    },
    drawFrom(cord) {
      this.ctx.beginPath();
      this.ctx.moveTo(this.xx, this.xy);
      this.ctx.lineTo(cord.x, cord.y)
      this.ctx.stroke();
      this.xx = cord.x;
      this.xy = cord.y;
    },
    sendMessage() {
      if (this.tekst != '') {
        this.socket.emit('message', this.tekst)
        this.tekst = '';
      }
    },
    playerReady() {
      this.socket.emit('readyUp')
      this.notReady = false
    },
    timeUp() {
      clearInterval(this.intervalid1)
      this.time = 30;
      this.socket.emit('roundEnded')
      this.eReady = false
      this.cetvrta = 0
    }
  }
};
</script>

<style scoped>
#dboard {
  margin: 0;
  padding: 0;
  overflow: hidden;
}
canvas {
  display: block;
  float: left;
  background-color: white;
  border: 4px solid black;
  margin: 0;
  padding: 0;
}
.other {
  display: block;
  float: left;
  width: 22%;
}
.paleta {
  display: block;
  float: left;
  width: 30%;
  height: 30vh;
}
.colButton {
  display: block;
  width: 100%;
  height: 16.6%;
}
#leaderboard {
  border: black 2px solid;
  display: block;
  float: left;
  padding: 0;
  width: 70%;
}
#leaderBox {
  list-style: none;
  padding: 0;
}
.ime {
  display: inline-block;
  width: 60%;
  border: 1px solid black;
  text-align: center;
}
.poeni {
  display: inline-block;
  width: 40%;
  border: solid 1px black;
}
#readyButton {
  font-size: 20px;
  display: block;
  width: 100%;
  background-color: #96ceb4;
  height: 2em;
}
#chat {
  display: block;
  width: 100%;
  float:left;
  border: 2px solid black;
  overflow: hidden;
}
#chatBox {
  border: 2px solid black;
  margin: 0;
  list-style: none;
  display: block;
  width: 100%;
}
#inputAndSend {
  display: block;
  width: 100%;
}
#messageInput {
  display: inline-block;
  width: 80%;
  font-size: 18px;
}
#sendButton {
  display: inline-block;
  width: 20%;
  background-color: #96ceb4;
  height: 25px;
}
#sendButton::after {
  display: none;
  content: '';
}
.sender {
  color: darkblue;
  display: inline-block;
  width: 25%;
  border: 1px solid black;
  font-size: 25px;
}
.messageText {
  display: inline-block;
  width: 75%;
  font-size: 25px;
  border: 1px solid black;
}
#misc {
  position: absolute;
  top: 1%;
  left: 1%;
  font-size: 30px;
}
</style>
