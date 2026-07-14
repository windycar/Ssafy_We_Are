<template>
  <div class="map">
    <h1>🗺️ 지도 화면</h1>

    <button @click="$router.push('/')">
      홈으로
    </button>
  </div>
</template>

<style scoped>
.map {
  text-align: center;
  margin-top: 100px;
}

button {
  padding: 15px 30px;
  font-size: 20px;
  border-radius: 10px;
  cursor: pointer;
}
</style>