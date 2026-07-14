let loading
export function loadKakaoMap(){
  if(window.kakao?.maps)return new Promise(resolve=>window.kakao.maps.load(()=>resolve(window.kakao)))
  if(loading)return loading
  loading=new Promise((resolve,reject)=>{const key=import.meta.env.VITE_KAKAO_MAP_API_KEY||import.meta.env.VITE_KAKAO_MAP_APP_KEY;if(!key)return reject(new Error('카카오 지도 API 키가 설정되지 않았습니다.'));const script=document.createElement('script');script.src=`https://dapi.kakao.com/v2/maps/sdk.js?appkey=${key}&autoload=false&libraries=clusterer,services`;script.onload=()=>window.kakao?.maps?.load(()=>resolve(window.kakao));script.onerror=()=>reject(new Error('카카오 지도 SDK를 불러오지 못했습니다.'));document.head.appendChild(script)})
  return loading
}
