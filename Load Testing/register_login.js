import http from 'k6/http';
import { check } from 'k6';

import { registerData as createDummyData } from './generateData';
import { htmlReport } from './htmlReport.bundle';

const baseBath = 'https://d73ehpcuydjzg.cloudfront.net/api/v1/auth';

const urls = {
  register: `${baseBath}/sign-up`,
  login: `${baseBath}/login`
}

export default function () {
  let data = createDummyData();

  let registerResp = http.post(urls.register,
    JSON.stringify(data),
    {
      headers: { 'Content-Type': 'application/json' },
    }
  );
  check(registerResp, { 'Signup Success': (r) => r.status == 200 });


  let loginRespFail = http.post(urls.login,
    JSON.stringify({ email: data.email, password: `${data.password}##incorrect` }),
    {
      headers: { 'Content-Type': 'application/json' },
    }
  );
  check(loginRespFail, {
    'Login incorrect passeword success': (r) => r.json("errorMessage") == 'Access to resources unauthorized'
  });


  let loginResp = http.post(urls.login,
    JSON.stringify({ email: data.email, password: data.password }),
    {
      headers: { 'Content-Type': 'application/json' },
    }
  );
  check(loginResp, { 'Login correct passeword success': (r) => r.status == 200 });
}

export function handleSummary(data) {
  const timeStamp = Date.now();
  return {
    [`./reports/summary-${timeStamp}.html`]: htmlReport(data),
  };
}

export const options = {
  scenarios: {
    mainRamp: {
      executor: 'ramping-arrival-rate',
      startRate: 50,
      timeUnit: '1s',

      stages: [
        { target: 100, duration: '5s' },
        { target: 200, duration: '10s' },
        { target: 200, duration: '20s' },
        { target: 0, duration: '5s' },
      ],
      preAllocatedVUs: '50',
      maxVUs: '99',
    },
  },

  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<1500'],
  },
  ext: {
    loadimpact: {
      name: 'Register and Login',
      projectID: 3666980,
    },
  },
};

