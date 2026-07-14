<template>
  <div class="home">
    <h1>🏠 안전 귀가 지도</h1>

    <button @click="$router.push('/map')">
      지도 보기
    </button>
  </div>
</template>

<style scoped>
.home {
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