<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { testScraperAuth, changePassword, type ScraperAuthStatus } from '@/api/settings'
import { getUsers, createUser, deleteUser, type User } from '@/api/users'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const scraperStatus = ref<ScraperAuthStatus | null>(null)
const scraperLoading = ref(false)

const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const pwSaving = ref(false)
const pwError = ref('')
const pwSuccess = ref(false)

async function loadScraperStatus() {
  scraperLoading.value = true
  try {
    scraperStatus.value = await testScraperAuth()
  } catch {
    scraperStatus.value = null
  } finally {
    scraperLoading.value = false
  }
}

async function submitPasswordChange() {
  pwError.value = ''
  pwSuccess.value = false
  if (newPassword.value !== confirmPassword.value) {
    pwError.value = 'Passwords do not match'
    return
  }
  if (newPassword.value.length < 8) {
    pwError.value = 'Password must be at least 8 characters'
    return
  }
  pwSaving.value = true
  try {
    await changePassword(currentPassword.value, newPassword.value)
    pwSuccess.value = true
    currentPassword.value = ''
    newPassword.value = ''
    confirmPassword.value = ''
  } catch (e: any) {
    pwError.value = e?.response?.data?.detail ?? 'Failed to change password'
  } finally {
    pwSaving.value = false
  }
}

// ── User Management ──────────────────────────────────────────────────────────
const users = ref<User[]>([])
const usersLoading = ref(false)
const usersError = ref('')

const newUsername = ref('')
const newUserPassword = ref('')
const newRole = ref<'admin' | 'viewer'>('viewer')
const addingUser = ref(false)
const addUserError = ref('')

async function loadUsers() {
  usersLoading.value = true
  usersError.value = ''
  try {
    users.value = await getUsers()
  } catch (e: any) {
    usersError.value = e?.response?.data?.detail ?? 'Failed to load users'
  } finally {
    usersLoading.value = false
  }
}

async function submitAddUser() {
  addUserError.value = ''
  addingUser.value = true
  try {
    await createUser({ username: newUsername.value, password: newUserPassword.value, role: newRole.value })
    newUsername.value = ''
    newUserPassword.value = ''
    newRole.value = 'viewer'
    await loadUsers()
  } catch (e: any) {
    addUserError.value = e?.response?.data?.detail ?? 'Failed to create user'
  } finally {
    addingUser.value = false
  }
}

async function removeUser(id: number) {
  try {
    await deleteUser(id)
    await loadUsers()
  } catch (e: any) {
    usersError.value = e?.response?.data?.detail ?? 'Failed to delete user'
  }
}

onMounted(() => {
  loadScraperStatus()
  if (auth.isAdmin) loadUsers()
})
</script>

<template>
  <div class="space-y-8">
    <!-- Header -->
    <div>
      <h1 style="font-family:'Orbitron',sans-serif; font-size:1.5rem; font-weight:700; color:var(--text-primary); letter-spacing:0.08em; text-transform:uppercase;">
        Settings
      </h1>
      <p style="font-family:'Share Tech Mono',monospace; font-size:0.75rem; color:var(--text-muted); margin-top:4px;">
        Account &amp; integration configuration
      </p>
    </div>

    <!-- Password Change -->
    <div class="glass-panel p-6 space-y-4">
      <h2 style="font-family:'Orbitron',sans-serif; font-size:0.85rem; font-weight:700; letter-spacing:0.12em; text-transform:uppercase; color:var(--neon-cyan);">
        Change Password
      </h2>

      <form @submit.prevent="submitPasswordChange" class="space-y-3 max-w-sm">
        <div>
          <label style="font-family:'Share Tech Mono',monospace; font-size:0.7rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.08em; display:block; margin-bottom:4px;">Current Password</label>
          <input
            v-model="currentPassword"
            type="password"
            autocomplete="current-password"
            required
            class="w-full px-3 py-2 rounded"
            style="background:rgba(0,0,0,0.45); border:1px solid rgba(255,184,0,0.18); color:var(--text-primary); font-family:'Share Tech Mono',monospace; font-size:0.85rem; outline:none;"
          />
        </div>
        <div>
          <label style="font-family:'Share Tech Mono',monospace; font-size:0.7rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.08em; display:block; margin-bottom:4px;">New Password</label>
          <input
            v-model="newPassword"
            type="password"
            autocomplete="new-password"
            required
            class="w-full px-3 py-2 rounded"
            style="background:rgba(0,0,0,0.45); border:1px solid rgba(255,184,0,0.18); color:var(--text-primary); font-family:'Share Tech Mono',monospace; font-size:0.85rem; outline:none;"
          />
        </div>
        <div>
          <label style="font-family:'Share Tech Mono',monospace; font-size:0.7rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.08em; display:block; margin-bottom:4px;">Confirm New Password</label>
          <input
            v-model="confirmPassword"
            type="password"
            autocomplete="new-password"
            required
            class="w-full px-3 py-2 rounded"
            style="background:rgba(0,0,0,0.45); border:1px solid rgba(255,184,0,0.18); color:var(--text-primary); font-family:'Share Tech Mono',monospace; font-size:0.85rem; outline:none;"
          />
        </div>

        <div v-if="pwError" style="font-family:'Share Tech Mono',monospace; font-size:0.75rem; color:var(--neon-pink);">
          {{ pwError }}
        </div>
        <div v-if="pwSuccess" style="font-family:'Share Tech Mono',monospace; font-size:0.75rem; color:var(--neon-green);">
          Password updated successfully.
        </div>

        <button
          type="submit"
          :disabled="pwSaving"
          class="px-5 py-2 rounded font-bold transition-all"
          style="font-family:'Orbitron',sans-serif; font-size:0.72rem; letter-spacing:0.1em; text-transform:uppercase; background:rgba(0,245,255,0.08); border:1px solid var(--neon-cyan); color:var(--neon-cyan); cursor:pointer;"
        >
          {{ pwSaving ? 'Saving…' : 'Update Password' }}
        </button>
      </form>
    </div>

    <!-- Scraper Status -->
    <div class="glass-panel p-6 space-y-4">
      <div class="flex items-center justify-between">
        <h2 style="font-family:'Orbitron',sans-serif; font-size:0.85rem; font-weight:700; letter-spacing:0.12em; text-transform:uppercase; color:var(--neon-cyan);">
          Scraper Connections
        </h2>
        <button
          @click="loadScraperStatus"
          :disabled="scraperLoading"
          class="px-3 py-1 rounded text-xs transition-all"
          style="font-family:'Share Tech Mono',monospace; background:rgba(255,184,0,0.06); border:1px solid rgba(255,184,0,0.2); color:var(--text-muted); cursor:pointer;"
        >
          {{ scraperLoading ? 'Testing…' : 'Re-test' }}
        </button>
      </div>

      <div v-if="scraperLoading" style="font-family:'Share Tech Mono',monospace; font-size:0.75rem; color:var(--text-muted);">
        Testing connections…
      </div>

      <div v-else-if="scraperStatus" class="grid gap-3 sm:grid-cols-2">
        <!-- ScreenScraper -->
        <div class="rounded-lg p-4 space-y-2" style="background:rgba(0,0,0,0.3); border:1px solid rgba(255,184,0,0.1);">
          <div class="flex items-center gap-2">
            <div
              class="w-2.5 h-2.5 rounded-full flex-shrink-0"
              :style="scraperStatus.screenscraper?.status === 'success'
                ? 'background:var(--neon-green); box-shadow:0 0 6px var(--neon-green)'
                : 'background:var(--neon-pink); box-shadow:0 0 6px var(--neon-pink)'"
            ></div>
            <span style="font-family:'Orbitron',sans-serif; font-size:0.7rem; font-weight:700; letter-spacing:0.1em; text-transform:uppercase; color:var(--text-primary);">ScreenScraper</span>
          </div>
          <p style="font-family:'Share Tech Mono',monospace; font-size:0.72rem; color:var(--text-muted);">
            {{ scraperStatus.screenscraper?.message ?? '—' }}
          </p>
          <p v-if="scraperStatus.screenscraper?.user" style="font-family:'Share Tech Mono',monospace; font-size:0.68rem; color:var(--text-muted); opacity:0.7;">
            user: {{ scraperStatus.screenscraper.user }}
          </p>
        </div>

        <!-- IGDB -->
        <div class="rounded-lg p-4 space-y-2" style="background:rgba(0,0,0,0.3); border:1px solid rgba(255,184,0,0.1);">
          <div class="flex items-center gap-2">
            <div
              class="w-2.5 h-2.5 rounded-full flex-shrink-0"
              :style="scraperStatus.igdb?.status === 'success'
                ? 'background:var(--neon-green); box-shadow:0 0 6px var(--neon-green)'
                : 'background:var(--neon-pink); box-shadow:0 0 6px var(--neon-pink)'"
            ></div>
            <span style="font-family:'Orbitron',sans-serif; font-size:0.7rem; font-weight:700; letter-spacing:0.1em; text-transform:uppercase; color:var(--text-primary);">IGDB</span>
          </div>
          <p style="font-family:'Share Tech Mono',monospace; font-size:0.72rem; color:var(--text-muted);">
            {{ scraperStatus.igdb?.message ?? '—' }}
          </p>
          <p v-if="scraperStatus.igdb?.client_id" style="font-family:'Share Tech Mono',monospace; font-size:0.68rem; color:var(--text-muted); opacity:0.7;">
            client: {{ scraperStatus.igdb.client_id }}
          </p>
        </div>
      </div>

      <div v-else style="font-family:'Share Tech Mono',monospace; font-size:0.75rem; color:var(--text-muted);">
        Could not reach backend.
      </div>
    </div>

    <!-- User Management (admin only) -->
    <div v-if="auth.isAdmin" class="glass-panel p-6 space-y-4">
      <h2 style="font-family:'Orbitron',sans-serif; font-size:0.85rem; font-weight:700; letter-spacing:0.12em; text-transform:uppercase; color:var(--neon-cyan);">
        User Management
      </h2>

      <!-- Error banner -->
      <div v-if="usersError" style="font-family:'Share Tech Mono',monospace; font-size:0.75rem; color:var(--neon-pink);">
        {{ usersError }}
      </div>

      <!-- User table -->
      <div v-if="usersLoading" style="font-family:'Share Tech Mono',monospace; font-size:0.75rem; color:var(--text-muted);">
        Loading users…
      </div>
      <table v-else-if="users.length" class="w-full" style="border-collapse:collapse;">
        <thead>
          <tr>
            <th style="font-family:'Share Tech Mono',monospace; font-size:0.68rem; text-transform:uppercase; letter-spacing:0.08em; color:var(--text-muted); text-align:left; padding-bottom:6px; border-bottom:1px solid rgba(255,184,0,0.15);">Username</th>
            <th style="font-family:'Share Tech Mono',monospace; font-size:0.68rem; text-transform:uppercase; letter-spacing:0.08em; color:var(--text-muted); text-align:left; padding-bottom:6px; border-bottom:1px solid rgba(255,184,0,0.15);">Role</th>
            <th style="font-family:'Share Tech Mono',monospace; font-size:0.68rem; text-transform:uppercase; letter-spacing:0.08em; color:var(--text-muted); text-align:left; padding-bottom:6px; border-bottom:1px solid rgba(255,184,0,0.15);">Created</th>
            <th style="border-bottom:1px solid rgba(255,184,0,0.15);"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in users" :key="u.id">
            <td style="font-family:'Share Tech Mono',monospace; font-size:0.78rem; color:var(--text-primary); padding:6px 0;">{{ u.username }}</td>
            <td style="padding:6px 0;">
              <span
                :style="u.role === 'admin'
                  ? 'font-family:\'Share Tech Mono\',monospace; font-size:0.7rem; color:var(--neon-pink); background:rgba(255,0,128,0.1); border:1px solid rgba(255,0,128,0.25); border-radius:4px; padding:1px 6px;'
                  : 'font-family:\'Share Tech Mono\',monospace; font-size:0.7rem; color:var(--text-muted); background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); border-radius:4px; padding:1px 6px;'"
              >{{ u.role }}</span>
            </td>
            <td style="font-family:'Share Tech Mono',monospace; font-size:0.72rem; color:var(--text-muted); padding:6px 0;">{{ new Date(u.created_at).toLocaleDateString() }}</td>
            <td style="padding:6px 0; text-align:right;">
              <button
                @click="removeUser(u.id)"
                :disabled="u.username === auth.user?.username"
                :style="{
                  fontFamily: '\'Share Tech Mono\',monospace',
                  fontSize: '0.68rem',
                  color: 'var(--neon-pink)',
                  background: 'rgba(255,0,128,0.06)',
                  border: '1px solid rgba(255,0,128,0.2)',
                  borderRadius: '4px',
                  padding: '2px 8px',
                  cursor: u.username === auth.user?.username ? 'not-allowed' : 'pointer',
                  opacity: u.username === auth.user?.username ? '0.35' : '1',
                }"
              >Delete</button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Add User form -->
      <div>
        <p style="font-family:'Orbitron',sans-serif; font-size:0.72rem; font-weight:700; letter-spacing:0.1em; text-transform:uppercase; color:var(--text-muted); margin-bottom:10px;">Add User</p>
        <form @submit.prevent="submitAddUser" class="flex flex-wrap gap-3 items-end">
          <div>
            <label style="font-family:'Share Tech Mono',monospace; font-size:0.65rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.08em; display:block; margin-bottom:3px;">Username</label>
            <input
              v-model="newUsername"
              type="text"
              minlength="3"
              maxlength="100"
              required
              placeholder="username"
              style="background:rgba(0,0,0,0.45); border:1px solid rgba(255,184,0,0.18); color:var(--text-primary); font-family:'Share Tech Mono',monospace; font-size:0.8rem; padding:6px 10px; border-radius:4px; outline:none; width:140px;"
            />
          </div>
          <div>
            <label style="font-family:'Share Tech Mono',monospace; font-size:0.65rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.08em; display:block; margin-bottom:3px;">Password</label>
            <input
              v-model="newUserPassword"
              type="password"
              minlength="8"
              required
              placeholder="min 8 chars"
              style="background:rgba(0,0,0,0.45); border:1px solid rgba(255,184,0,0.18); color:var(--text-primary); font-family:'Share Tech Mono',monospace; font-size:0.8rem; padding:6px 10px; border-radius:4px; outline:none; width:140px;"
            />
          </div>
          <div>
            <label style="font-family:'Share Tech Mono',monospace; font-size:0.65rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.08em; display:block; margin-bottom:3px;">Role</label>
            <select
              v-model="newRole"
              style="background:rgba(0,0,0,0.55); border:1px solid rgba(255,184,0,0.18); color:var(--text-primary); font-family:'Share Tech Mono',monospace; font-size:0.8rem; padding:6px 10px; border-radius:4px; outline:none;"
            >
              <option value="viewer">viewer</option>
              <option value="admin">admin</option>
            </select>
          </div>
          <button
            type="submit"
            :disabled="addingUser"
            style="font-family:'Orbitron',sans-serif; font-size:0.7rem; letter-spacing:0.08em; text-transform:uppercase; background:rgba(0,245,255,0.08); border:1px solid var(--neon-cyan); color:var(--neon-cyan); padding:6px 14px; border-radius:4px; cursor:pointer;"
          >{{ addingUser ? 'Creating…' : 'Create' }}</button>
        </form>
        <p v-if="addUserError" style="font-family:'Share Tech Mono',monospace; font-size:0.72rem; color:var(--neon-pink); margin-top:6px;">{{ addUserError }}</p>
      </div>
    </div>

    <!-- About -->
    <div class="glass-panel p-6 space-y-3">
      <h2 style="font-family:'Orbitron',sans-serif; font-size:0.85rem; font-weight:700; letter-spacing:0.12em; text-transform:uppercase; color:var(--neon-cyan);">
        About JARL
      </h2>
      <div class="space-y-1" style="font-family:'Share Tech Mono',monospace; font-size:0.75rem; color:var(--text-muted);">
        <p>Just Another ROM Library — self-hosted metadata manager</p>
        <p>
          <a
            href="https://github.com/DavidSchuchert/JARL---Jet-Another-Rom-Library"
            target="_blank"
            rel="noopener"
            style="color:var(--neon-cyan); text-decoration:underline;"
          >
            github.com/DavidSchuchert/JARL
          </a>
        </p>
        <p style="margin-top:8px; font-size:0.68rem; opacity:0.5;">MIT License</p>
      </div>
    </div>
  </div>
</template>
