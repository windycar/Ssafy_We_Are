<template>
  <div class="app">

    <!-- 상단 메뉴 -->
    <header class="header">

      <div class="logo">
        🛡 SAFE HOME
      </div>

      <nav>
        <a href="#">홈</a>
        <a href="#">안전지도</a>
        <a href="#">커뮤니티</a>
        <a href="#">AI 챗봇</a>
      </nav>

    </header>


    <!-- 메인 화면 -->
    <section class="hero">

      <div class="hero-text">

        <h1>
          안전한 귀가를 위한<br>
          스마트 안전 지도 서비스
        </h1>

        <p>
          내 주변 CCTV와 경찰관서를 확인하고<br>
          AI 챗봇과 함께 더 안전한 길을 찾아보세요.
        </p>


        <button @click="$router.push('/map')">
          🗺 안전지도 시작하기
        </button>

      </div>


      <div class="hero-card">

        <div class="map-box">

          📍

          <div class="marker cctv">
            📷
          </div>

          <div class="marker police">
            🚓
          </div>

          <div class="marker safe">
            🟢
          </div>

        </div>

      </div>

    </section>



    <!-- 기능 카드 -->
    <section class="features">

      <h2>
        주요 기능
      </h2>


      <div class="card-container">


        <div class="card">
          <div class="icon">
            🗺
          </div>

          <h3>
            안전 지도
          </h3>

          <p>
            현재 위치 기반<br>
            CCTV와 경찰서 정보를 제공합니다.
          </p>

        </div>



        <div class="card">

          <div class="icon">
            🔥
          </div>

          <h3>
            치안 히트맵
          </h3>

          <p>
            지역별 안전도를<br>
            한눈에 확인합니다.
          </p>

        </div>




        <div class="card">

          <div class="icon">
            🤖
          </div>

          <h3>
            AI 안전 챗봇
          </h3>

          <p>
            주변 안전시설과<br>
            정보를 안내합니다.
          </p>

        </div>



        <div class="card">

          <div class="icon">
            📢
          </div>

          <h3>
            익명 커뮤니티
          </h3>

          <p>
            지역 위험 정보를<br>
            공유합니다.
          </p>

        </div>


      </div>

    </section>



    <!-- 하단 -->
    <footer>

      © 2026 SAFE HOME

    </footer>

<router-view />

  </div>
</template>


<style>

* {
  box-sizing: border-box;
}


body {

  margin:0;

  font-family:
  'Pretendard',
  Arial,
  sans-serif;

  background:#f8fafc;

}



.header {

  height:80px;

  display:flex;

  justify-content:space-between;

  align-items:center;

  padding:0 80px;

  background:white;

  box-shadow:
  0 3px 15px rgba(0,0,0,0.05);

}



.logo {

  font-size:24px;

  font-weight:800;

  color:#1e3a8a;

}



nav a {

  margin-left:35px;

  text-decoration:none;

  color:#334155;

  font-weight:600;

}




.hero {

  display:flex;

  justify-content:center;

  align-items:center;

  gap:80px;

  padding:100px 80px;

}



.hero-text h1 {

  font-size:40px;

  line-height:1.3;

  color:#0f172a;

}



.hero-text p {

  color:#64748b;

  font-size:18px;

  line-height:1.8;

}



button {

  margin-top:30px;

  background:#2563eb;

  color:white;

  border:none;

  padding:16px 30px;

  border-radius:15px;

  font-size:16px;

  cursor:pointer;

}




.map-box {


  width:420px;

  height:350px;

  background:
  linear-gradient(
    135deg,
    #dbeafe,
    #eff6ff
  );

  border-radius:30px;

  display:flex;

  justify-content:center;

  align-items:center;

  font-size:80px;

  position:relative;

}



.marker {

 position:absolute;

 font-size:35px;

}


.cctv {

 top:60px;

 left:80px;

}


.police {

 right:80px;

 top:120px;

}



.safe {

 bottom:80px;

}




.features {

 padding:60px 80px;

 text-align:center;

}



.features h2 {

 font-size:35px;

}



.card-container {

 display:flex;

 justify-content:center;

 gap:25px;

 margin-top:40px;

}



.card {


 width:260px;

 background:white;

 padding:35px;

 border-radius:25px;

 box-shadow:
 0 10px 30px rgba(0,0,0,0.08);


 transition:.3s;

}



.card:hover {

 transform:translateY(-10px);

}



.icon {

 font-size:45px;

}


.card h3 {

 color:#1e3a8a;

}



.card p {

 color:#64748b;

 line-height:1.6;

}



footer {

 text-align:center;

 padding:30px;

 color:#64748b;

}


</style>