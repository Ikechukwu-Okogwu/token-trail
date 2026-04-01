import { Link } from 'react-router-dom'
import {
  FileText, GraduationCap, BookOpen,
  Zap, ShieldCheck, Columns,
  ClipboardList, Upload, BarChart3,
} from 'lucide-react'

const FEATURES = [
  {
    icon: Zap,
    title: 'Fast Analysis',
    desc: 'Token-based comparison runs in seconds, even on large class sizes.',
  },
  {
    icon: ShieldCheck,
    title: 'Smart Detection',
    desc: 'Catches renamed variables, reordered functions, and template code.',
  },
  {
    icon: Columns,
    title: 'Clear Comparisons',
    desc: 'Side-by-side code views with highlighted matching regions.',
  },
]

const STEPS = [
  { num: 1, icon: ClipboardList, title: 'Create Assignment', desc: 'Set up a course, create an assignment, and share the unique key with students.' },
  { num: 2, icon: Upload, title: 'Students Upload Code', desc: 'Students submit their ZIP files using the assignment key — no login required.' },
  { num: 3, icon: BarChart3, title: 'Run Analysis & Review', desc: 'Queue an analysis run, view ranked similarity pairs, and drill into side-by-side comparisons.' },
]

function MockCodePane({ label, lines, highlights }) {
  return (
    <div className="flex-1 min-w-0 overflow-hidden rounded-lg border border-gray-200 bg-white">
      <div className="border-b border-gray-100 bg-gray-50 px-3 py-1.5 text-xs font-medium text-gray-500">
        {label}
      </div>
      <pre className="p-3 text-xs leading-5 text-gray-600 overflow-x-auto">
        {lines.map((line, i) => (
          <div
            key={i}
            className={`flex gap-3 px-1 -mx-1 rounded-sm ${highlights.includes(i) ? 'bg-brand-purple/10 text-brand-purple' : ''}`}
          >
            <span className="w-5 shrink-0 text-right text-gray-300 select-none">{i + 1}</span>
            <span className="whitespace-pre">{line}</span>
          </div>
        ))}
      </pre>
    </div>
  )
}

export default function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col bg-brand-pink/40">
      {/* Header */}
      <header className="flex h-16 items-center justify-between bg-brand-purple px-8 shadow-md">
        <div className="flex items-center gap-2">
          <FileText className="h-6 w-6 text-white" />
          <span className="text-xl font-semibold text-white tracking-tight">Token Trail</span>
        </div>
        <div className="flex items-center gap-3">
          <Link
            to="/login"
            className="rounded-full border border-white/30 bg-white/10 px-4 py-1.5 text-sm font-medium text-white backdrop-blur-sm transition-all hover:bg-white/20"
          >
            Sign In
          </Link>
          <Link
            to="/login"
            className="rounded-full bg-white px-4 py-1.5 text-sm font-medium text-brand-purple transition-all hover:bg-brand-pink"
          >
            Sign Up
          </Link>
        </div>
      </header>

      {/* Hero + Cards — single container, gradient fade creates the bridge effect */}
      <div className="relative bg-landing px-6 pt-20 pb-14 text-center">
        <h1 className="relative z-10 text-4xl font-bold tracking-tight text-white sm:text-5xl">
          Academic integrity,<br />powered by code analysis
        </h1>
        <p className="relative z-10 mx-auto mt-4 max-w-xl text-lg leading-relaxed text-white/75">
          Token Trail helps universities detect code similarity with transparent,
          token-based analysis. Fast results. Fair assessments.
        </p>

        {/* Cards — z-10 keeps them above the gradient overlay */}
        <div className="relative z-10 mx-auto mt-12 translate-y-6 grid w-full max-w-xl gap-4 sm:grid-cols-2">
          {/* Subtle glow behind both cards */}
          <div className="pointer-events-none absolute left-1/2 top-1/2 h-[200px] w-[400px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-purple-400/10 blur-3xl" />
          <Link
            to="/login"
            className="group flex flex-col items-center gap-4 rounded-2xl border border-white/60 bg-white p-8 ring-1 ring-black/5 shadow-lg transition-all duration-300 hover:-translate-y-0.5 hover:shadow-2xl"
          >
            <div className="flex h-14 w-14 items-center justify-center rounded-full bg-brand-purple/10 transition-colors group-hover:bg-brand-purple/20">
              <BookOpen className="h-7 w-7 text-brand-purple" />
            </div>
            <div className="text-center">
              <h2 className="text-lg font-semibold text-gray-900">Instructor</h2>
              <p className="mt-1 text-sm text-gray-500">
                Create courses, manage assignments, and run similarity analysis
              </p>
            </div>
            <span className="text-sm font-medium text-brand-purple group-hover:underline underline-offset-2">
              Sign in &rarr;
            </span>
          </Link>

          <Link
            to="/student-submit"
            className="group flex flex-col items-center gap-4 rounded-2xl border border-white/60 bg-white p-8 ring-1 ring-black/5 shadow-lg transition-all duration-300 hover:-translate-y-0.5 hover:shadow-2xl"
          >
            <div className="flex h-14 w-14 items-center justify-center rounded-full bg-brand-purple/10 transition-colors group-hover:bg-brand-purple/20">
              <GraduationCap className="h-7 w-7 text-brand-purple" />
            </div>
            <div className="text-center">
              <h2 className="text-lg font-semibold text-gray-900">Student</h2>
              <p className="mt-1 text-sm text-gray-500">
                Submit your code using an assignment key from your instructor
              </p>
            </div>
            <span className="text-sm font-medium text-brand-purple group-hover:underline underline-offset-2">
              Submit code &rarr;
            </span>
          </Link>
        </div>

        {/* Gradient overlay — fades bottom half of card zone from purple into the page bg */}
        <div className="pointer-events-none absolute inset-x-0 bottom-0 h-72 bg-gradient-to-b from-transparent via-brand-pink/25 to-brand-pink/40" />
      </div>

      {/* ── Value proposition ── */}
      <section className="bg-white px-6 py-20">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight text-gray-900">
            Detect code similarity with confidence
          </h2>
          <p className="mt-4 text-base leading-relaxed text-gray-500">
            Token Trail helps instructors identify potential plagiarism through
            structured code analysis and clear, side-by-side comparisons — so you
            can make fair decisions backed by evidence.
          </p>
        </div>

        {/* Feature cards */}
        <div className="mx-auto mt-14 grid max-w-3xl gap-8 sm:grid-cols-3">
          {FEATURES.map((f) => (
            <div key={f.title} className="flex flex-col items-center text-center">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-brand-purple/10">
                <f.icon className="h-6 w-6 text-brand-purple" />
              </div>
              <h3 className="mt-4 text-sm font-semibold text-gray-900">{f.title}</h3>
              <p className="mt-1.5 text-sm leading-relaxed text-gray-500">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── How It Works ── */}
      <section className="relative overflow-hidden bg-brand-pink/50 px-6 py-20">
        <div className="pointer-events-none absolute -right-32 bottom-0 h-72 w-72 rounded-full bg-brand-purple/5 blur-3xl" />
        <div className="mx-auto max-w-3xl">
          <h2 className="text-center text-3xl font-bold tracking-tight text-gray-900">
            How it works
          </h2>
          <p className="mt-3 text-center text-base text-gray-500">
            Three steps from assignment creation to actionable results.
          </p>

          <div className="relative mt-14 grid gap-10 sm:grid-cols-3">
            {/* Connector line (desktop) */}
            <div className="pointer-events-none absolute top-7 left-[16.67%] right-[16.67%] hidden h-px bg-brand-purple/20 sm:block" />

            {STEPS.map((s) => (
              <div key={s.num} className="relative flex flex-col items-center text-center">
                <div className="relative z-10 flex h-14 w-14 items-center justify-center rounded-full border-2 border-brand-purple/20 bg-white shadow-sm">
                  <s.icon className="h-6 w-6 text-brand-purple" />
                </div>
                <span className="mt-1 text-xs font-semibold text-brand-purple/60">Step {s.num}</span>
                <h3 className="mt-2 text-sm font-semibold text-gray-900">{s.title}</h3>
                <p className="mt-1.5 text-sm leading-relaxed text-gray-500">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Product preview mock ── */}
      <section className="bg-white px-6 py-20">
        <div className="mx-auto max-w-3xl">
          <h2 className="text-center text-3xl font-bold tracking-tight text-gray-900">
            See the evidence clearly
          </h2>
          <p className="mt-3 text-center text-base text-gray-500">
            Drill into any flagged pair to review matched code regions side by side.
          </p>

          {/* Mock comparison card */}
          <div className="mt-12 overflow-hidden rounded-2xl border border-gray-200 bg-gray-50 shadow-lg">
            {/* Mock header bar */}
            <div className="flex items-center justify-between border-b border-gray-200 bg-brand-purple px-5 py-3">
              <div className="flex items-center gap-2 text-sm font-medium text-white">
                <Columns className="h-4 w-4" />
                Submission A vs Submission B
              </div>
              <span className="rounded-full bg-red-500/90 px-3 py-0.5 text-xs font-bold text-white">
                93.5% Similar
              </span>
            </div>

            {/* Mock advisory */}
            <div className="border-b border-gray-200 bg-amber-50 px-5 py-2 text-xs text-amber-700">
              Advisory: Similarity scores indicate structural overlap and are not proof of misconduct.
            </div>

            {/* Side-by-side code */}
            <div className="flex flex-col gap-px bg-gray-200 sm:flex-row">
              <MockCodePane
                label="student_a / LinkedList.java"
                lines={[
                  'public class LinkedList {',
                  '  private Node head;',
                  '',
                  '  public void insert(int val) {',
                  '    Node n = new Node(val);',
                  '    n.next = head;',
                  '    head = n;',
                  '  }',
                  '',
                  '  public int size() {',
                  '    int count = 0;',
                  '    Node cur = head;',
                  '    while (cur != null) {',
                  '      count++;',
                  '      cur = cur.next;',
                  '    }',
                  '    return count;',
                  '  }',
                  '}',
                ]}
                highlights={[3, 4, 5, 6, 9, 10, 11, 12, 13, 14]}
              />
              <MockCodePane
                label="student_b / MyList.java"
                lines={[
                  'public class MyList {',
                  '  private Node first;',
                  '',
                  '  public void add(int value) {',
                  '    Node node = new Node(value);',
                  '    node.next = first;',
                  '    first = node;',
                  '  }',
                  '',
                  '  public int length() {',
                  '    int cnt = 0;',
                  '    Node tmp = first;',
                  '    while (tmp != null) {',
                  '      cnt++;',
                  '      tmp = tmp.next;',
                  '    }',
                  '    return cnt;',
                  '  }',
                  '}',
                ]}
                highlights={[3, 4, 5, 6, 9, 10, 11, 12, 13, 14]}
              />
            </div>
          </div>

          <p className="mt-4 text-center text-xs text-gray-400">
            Mock preview — actual results are generated from your students&apos; submissions.
          </p>
        </div>
      </section>

      {/* ── Bottom CTA ── */}
      <section className="relative overflow-hidden bg-landing px-6 py-16 text-center">
        <div className="pointer-events-none absolute left-1/2 top-0 h-full w-[140%] -translate-x-1/2 bg-[radial-gradient(ellipse_at_center,rgba(255,255,255,0.08),transparent_70%)]" />
        <h2 className="relative text-2xl font-bold text-white sm:text-3xl">
          Ready to get started?
        </h2>
        <p className="relative mt-3 text-sm text-white/70">
          Create your instructor account and run your first analysis in minutes.
        </p>
        <div className="relative mt-6 flex items-center justify-center gap-4">
          <Link
            to="/login"
            className="rounded-full bg-white px-6 py-2.5 text-sm font-semibold text-brand-purple shadow-lg transition-all hover:shadow-xl hover:scale-105"
          >
            Get Started
          </Link>
          <Link
            to="/student-submit"
            className="rounded-full border border-white/30 bg-white/10 px-6 py-2.5 text-sm font-medium text-white backdrop-blur-sm transition-all hover:bg-white/20"
          >
            Submit Code
          </Link>
        </div>
      </section>

      <footer className="border-t border-brand-purple/10 bg-white py-6 text-center text-xs text-gray-400">
        &copy; {new Date().getFullYear()} Token Trail. Built for academic integrity.
      </footer>
    </div>
  )
}
