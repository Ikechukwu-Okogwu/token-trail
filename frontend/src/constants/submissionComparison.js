/**
 * Dummy data for submission comparison view.
 * Replace with API calls when backend implements similarity endpoints.
 */

export const DUMMY_SUBMISSION_ID = 'dummy-submission-id'

export const DUMMY_STUDENT_DETAILS = {
  name: 'John Doe',
  studentNumber: '111111',
  files: 5,
  submissionDate: '01/01/26 23:59',
}

export const DUMMY_METRICS = {
  codeSimilarity: 73,
  commonFiles: 4,
  matchingLines: 142,
}

export const DUMMY_SIMILARITY_CANDIDATES = [
  { resultId: 'r1', studentName: 'Jon Snow', similarityScore: 72 },
  { resultId: 'r2', studentName: 'Jane Doe', similarityScore: 70 },
  { resultId: 'r3', studentName: 'student', similarityScore: 66 },
  { resultId: 'r4', studentName: 'student', similarityScore: 53 },
  { resultId: 'r5', studentName: 'student', similarityScore: 41 },
  { resultId: 'r6', studentName: 'student', similarityScore: 40 },
  { resultId: 'r7', studentName: 'student', similarityScore: 38 },
  { resultId: 'r8', studentName: 'student', similarityScore: 38 },
  { resultId: 'r9', studentName: 'student', similarityScore: 14 },
]

export const DUMMY_FILES = [
  'Main.java',
  'Player.java',
  'Room.java',
  'Monster.java',
  'GameLogic.java',
]

export const DUMMY_CODE_CONTENT = `import java.util.*;

public class MiniDungeon {
  public static void main(String[] args) {
    String[] rooms = {"entrance", "hall", "treasure"};
    String[] monsters = {"goblin", "dragon"};
    String[] items = {"sword", "shield", "potion"};

    int playerHp = 100;
    List<String> inventory = new ArrayList<>();
    int position = 0;

    System.out.println("Welcome to the Mini Dungeon!");
    System.out.println("Type: move, search, rest, or quit");
  }
}`
