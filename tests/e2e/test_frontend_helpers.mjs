/**
 * Verifies the frontend API helpers work by making the same requests they would.
 * Run: node tests/e2e/test_frontend_helpers.mjs
 * Requires: Docker stack running (backend at localhost:8000)
 */
const API_BASE = process.env.API_BASE_URL || 'http://localhost:8000/api';

async function apiFetch(path, options = {}) {
  const url = `${API_BASE}${path}`;
  const headers = { ...options.headers };
  if (options.token) {
    headers['Authorization'] = `Bearer ${options.token}`;
  }
  if (options.body && !(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }
  const res = await fetch(url, { ...options, headers });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

async function main() {
  const errors = [];
  let token;
  let assignmentId;
  let runId;

  try {
    // 1. Signup (simulates getting token for localStorage)
    const signupRes = await fetch(`${API_BASE}/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: 'Helper Test User',
        email: `helper-test-${Date.now()}@example.com`,
        password: 'secret123',
      }),
    });
    if (!signupRes.ok) throw new Error(`Signup failed: ${signupRes.status}`);
    const signupData = await signupRes.json();
    token = signupData.accessToken;
    console.log('✓ Signup -> token received');

    // 2. getInstructorAssignmentById - need to create assignment first
    const courseRes = await apiFetch('/instructor/courses', {
      method: 'POST',
      body: JSON.stringify({ name: 'Helper Test', term: 'T1' }),
      token,
    });
    const courseId = courseRes.id;

    const assignRes = await apiFetch('/instructor/assignments', {
      method: 'POST',
      body: JSON.stringify({
        courseId,
        title: 'HW1',
        language: 'java',
        isOpen: true,
        dueDate: null,
        keyExpiry: null,
        autoAnalysis: false,
        allowLate: false,
        exclusionCode: null,
      }),
      token,
    });
    assignmentId = assignRes.id;
    console.log('✓ Create assignment ->', assignmentId);

    // 3. getInstructorAssignmentById
    const assignment = await apiFetch(`/instructor/assignments/${assignmentId}`, { token });
    if (!assignment.id || assignment.id !== assignmentId) throw new Error('getInstructorAssignmentById: wrong response');
    console.log('✓ getInstructorAssignmentById works');

    // 4. getAssignmentSubmissions
    const submissions = await apiFetch(`/instructor/assignments/${assignmentId}/submissions`, { token });
    if (!Array.isArray(submissions)) throw new Error('getAssignmentSubmissions: expected array');
    console.log('✓ getAssignmentSubmissions works');

    // 5. queueAnalysisRun
    const runRes = await apiFetch(`/instructor/assignments/${assignmentId}/analysis-runs`, {
      method: 'POST',
      token,
    });
    runId = runRes.runId;
    if (!runId) throw new Error('queueAnalysisRun: no runId');
    console.log('✓ queueAnalysisRun works');

    // 6. getAnalysisRunStatus
    const runStatus = await apiFetch(`/instructor/analysis-runs/${runId}`, { token });
    if (!runStatus.runId || runStatus.runId !== runId) throw new Error('getAnalysisRunStatus: wrong response');
    console.log('✓ getAnalysisRunStatus works');

    // 7. Verify no token -> 401/403
    try {
      await apiFetch(`/instructor/assignments/${assignmentId}`);
      errors.push('Expected 401/403 when no token');
    } catch (e) {
      const msg = e.message.toLowerCase();
      if (msg.includes('401') || msg.includes('403') || msg.includes('not authenticated') || msg.includes('authenticated')) {
        console.log('✓ Auth required when no token');
      } else {
        throw e;
      }
    }

    console.log('\nAll frontend API helpers work correctly.');
    process.exit(0);
  } catch (err) {
    console.error('\nHelper check failed:', err.message);
    if (errors.length) console.error('Additional errors:', errors);
    process.exit(1);
  }
}

main();
