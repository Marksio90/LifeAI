import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const chatResponseTime = new Trend('chat_response_time');
const streamingTime = new Trend('streaming_time');

// Test configuration
export const options = {
  stages: [
    { duration: '2m', target: 50 },    // Ramp-up to 50 users
    { duration: '5m', target: 50 },    // Stay at 50 for 5 minutes
    { duration: '2m', target: 100 },   // Ramp-up to 100 users
    { duration: '5m', target: 100 },   // Stay at 100 for 5 minutes
    { duration: '2m', target: 200 },   // Spike to 200 users
    { duration: '1m', target: 200 },   // Stay at spike
    { duration: '2m', target: 0 },     // Ramp-down to 0
  ],
  thresholds: {
    'http_req_duration': ['p(95)<500', 'p(99)<1000'], // 95% < 500ms, 99% < 1s
    'http_req_failed': ['rate<0.01'],  // Error rate < 1%
    'errors': ['rate<0.05'],           // Custom error rate < 5%
    'chat_response_time': ['p(95)<2000'], // Chat response < 2s for 95%
  },
  ext: {
    loadimpact: {
      projectID: 3636739,
      name: 'LifeAI API Load Test',
      distribution: {
        'amazon:us:ashburn': { loadZone: 'amazon:us:ashburn', percent: 50 },
        'amazon:eu:dublin': { loadZone: 'amazon:eu:dublin', percent: 50 },
      },
    },
  },
};

const BASE_URL = __ENV.BASE_URL || 'https://api.lifeai.com';

// User credentials
const users = [
  { email: 'test1@example.com', password: 'testpass123' },
  { email: 'test2@example.com', password: 'testpass123' },
  { email: 'test3@example.com', password: 'testpass123' },
];

function randomUser() {
  return users[Math.floor(Math.random() * users.length)];
}

function randomMessage() {
  const messages = [
    'How can I save money this month?',
    'I need help with my budget',
    'What are good exercises for weight loss?',
    'How do I improve my relationship with my partner?',
    'What career path should I choose?',
    'Help me plan my day',
    'I feel stressed, what should I do?',
    'How to be more productive?',
  ];
  return messages[Math.floor(Math.random() * messages.length)];
}

export function setup() {
  // Setup: Login and get tokens for test users
  console.log('Setting up test data...');

  const tokens = [];
  for (const user of users) {
    const res = http.post(`${BASE_URL}/api/auth/login`, JSON.stringify({
      email: user.email,
      password: user.password,
    }), {
      headers: { 'Content-Type': 'application/json' },
    });

    if (res.status === 200) {
      const token = JSON.parse(res.body).access_token;
      tokens.push(token);
    }
  }

  return { tokens };
}

export default function (data) {
  const token = data.tokens[Math.floor(Math.random() * data.tokens.length)];

  const params = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    tags: { name: 'ChatAPI' },
  };

  // =========================================================================
  // Test 1: Start Chat Session
  // =========================================================================
  group('Start Chat Session', function () {
    const sessionRes = http.post(
      `${BASE_URL}/api/chat/start`,
      JSON.stringify({}),
      params
    );

    check(sessionRes, {
      'session created': (r) => r.status === 200,
      'session has ID': (r) => JSON.parse(r.body).session_id !== undefined,
    }) || errorRate.add(1);

    if (sessionRes.status === 200) {
      const sessionId = JSON.parse(sessionRes.body).session_id;

      // =========================================================================
      // Test 2: Send Message
      // =========================================================================
      group('Send Message', function () {
        const messageStart = Date.now();

        const messageRes = http.post(
          `${BASE_URL}/api/chat/message`,
          JSON.stringify({
            session_id: sessionId,
            message: randomMessage(),
            modality: 'text',
          }),
          params
        );

        const messageDuration = Date.now() - messageStart;
        chatResponseTime.add(messageDuration);

        check(messageRes, {
          'message sent': (r) => r.status === 200,
          'response has content': (r) => {
            const body = JSON.parse(r.body);
            return body.response && body.response.length > 0;
          },
          'response time acceptable': (r) => messageDuration < 5000,
        }) || errorRate.add(1);
      });

      // =========================================================================
      // Test 3: Get Conversation History
      // =========================================================================
      group('Get History', function () {
        const historyRes = http.get(
          `${BASE_URL}/api/chat/history/${sessionId}`,
          params
        );

        check(historyRes, {
          'history retrieved': (r) => r.status === 200,
          'history not empty': (r) => JSON.parse(r.body).messages.length > 0,
        }) || errorRate.add(1);
      });

      // =========================================================================
      // Test 4: Rate Limiting Check
      // =========================================================================
      group('Rate Limit', function () {
        const rateLimitRes = http.get(
          `${BASE_URL}/api/chat/history/${sessionId}`,
          params
        );

        check(rateLimitRes, {
          'has rate limit headers': (r) =>
            r.headers['X-Ratelimit-Limit'] !== undefined &&
            r.headers['X-Ratelimit-Remaining'] !== undefined,
        });
      });

      // =========================================================================
      // Test 5: End Session
      // =========================================================================
      group('End Session', function () {
        const endRes = http.post(
          `${BASE_URL}/api/chat/end`,
          JSON.stringify({ session_id: sessionId }),
          params
        );

        check(endRes, {
          'session ended': (r) => r.status === 200,
        }) || errorRate.add(1);
      });
    }
  });

  // =========================================================================
  // Test 6: Dashboard Analytics
  // =========================================================================
  group('Dashboard Analytics', function () {
    const analyticsRes = http.get(
      `${BASE_URL}/api/analytics/dashboard?range=7d`,
      params
    );

    check(analyticsRes, {
      'analytics loaded': (r) => r.status === 200,
      'has statistics': (r) => {
        const body = JSON.parse(r.body);
        return body.totalConversations !== undefined;
      },
    }) || errorRate.add(1);
  });

  // =========================================================================
  // Test 7: Health Check
  // =========================================================================
  group('Health Check', function () {
    const healthRes = http.get(`${BASE_URL}/health/ready`);

    check(healthRes, {
      'service is healthy': (r) => r.status === 200,
      'db is connected': (r) => {
        const body = JSON.parse(r.body);
        return body.checks && body.checks.database === true;
      },
    });
  });

  // Think time: simulate real user behavior
  sleep(Math.random() * 3 + 1); // 1-4 seconds
}

export function teardown(data) {
  console.log('Tearing down...');
  console.log(`Test completed with ${data.tokens.length} users`);
}

// =========================================================================
// Custom Thresholds Summary
// =========================================================================
export function handleSummary(data) {
  console.log('Test Summary:');
  console.log(`  Total Requests: ${data.metrics.http_reqs.values.count}`);
  console.log(`  Failed Requests: ${data.metrics.http_req_failed.values.rate * 100}%`);
  console.log(`  Avg Response Time: ${data.metrics.http_req_duration.values.avg}ms`);
  console.log(`  P95 Response Time: ${data.metrics.http_req_duration.values['p(95)']}ms`);

  return {
    'summary.json': JSON.stringify(data),
    'stdout': textSummary(data, { indent: ' ', enableColors: true }),
  };
}
