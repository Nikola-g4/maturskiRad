<template>
  <div id="app">
    <DrawingBoard :usr="username" :code="this.roomName" v-if="nameGiven" class="brd"/>
    <div id="nameInputField" v-else>            
      <input v-model="username" type="text" placeholder="👤: Upišite nadimak" class="textField field" id="nickField"/>       
      <input type="text" v-model="roomName" placeholder="🏠: Upišite kod sobe" class="textField field" id="roomField" title="Napravite sobu a onda podelite kod sa svojim prijateljima">     
      <p class="center">
      <button v-on:click="sendName()" id="continueButton" class="field">Nastavi</button>
      </p>
    </div>
  </div>
</template>

<script>
import DrawingBoard from "./components/DrawingBoard";

export default {
  name: "App",
  components: {
    DrawingBoard,
  },
  data() {
    return {
      nameGiven: false,
      componentKey: 0,
      username: '',
      roomName: ''      
    };
  },
  methods: {
    sendName() {      
      if (this.username != '' && this.roomName != '')
      {
        this.nameGiven = true;
        this.componentKey += 1;
      }
    },
  },
};
</script>

<style>
* {
  box-sizing: border-box;
}
html {
  font-size: 25px;
  background-color: lightgray;
}
@keyframes fadeIn {
  from {opacity: 0;
  transform: translate(-40%, -40%);}
  to {opacity: 1;
  transform: translate(-50%, -70%);}
}
#nameInputField {
  position: absolute;
  left: 50%;
  top: 50%;  
  border: 5px solid black;
  transform: translate(-50%, -70%);
  padding: 10px;
  border-radius: 10%;
  background-color: #8d9db6;
  color: white;
  animation-name: fadeIn;
  animation-duration: 1.8s;
}
.field {
  display: block;
  margin-bottom: 10px;
}
.textField {
  width: 90%;
  padding: 5px;
  font-size: 20px;
}
#continueButton {
  background-color: #96ceb4;
  color: black;
  width: 10em;
  height: 2em;
  display: inline-block;
}
.center {
  text-align: center;
  margin: 0;  
}
</style>
