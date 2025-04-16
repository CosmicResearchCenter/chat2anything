import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import { getRequest } from '../utils/http'
// import KnowledgeBaseManager from '../views/KnowledgeBaseManager/KnowledgeBaseManager.vue'
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path:"/login",
      name:"login",
      component: () => import('../views/Account/LoginView.vue')
    },
    {
      path:"/admin",
      name:"admin",
      component: () => import('../views/Account/AdminView.vue')
    },
    {
      path:"/admin/chat",
      name:"admin_chat",
      component: () => import('../views/Account/AdminChatView.vue')
    },
    {
      path:"/admin/base",
      name:"admin_base",
      component: () => import('../views/Account/AdminBaseView.vue')
    },
    {
      path:"/admin/user",
      name:"admin_user",
      component: () => import('../views/Account/AdminUserView.vue')
    },
    {
      path: '/manager',
      name: 'manager',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/KnowledgeBaseListView.vue')
    },
    {
      path: '/manager/:base_id',
      name: 'knowledge-base',
      component: () => import('../views/KnowledgeBaseManager/KnowledgeBaseManager.vue')
    },
    
    {
      path: '/manager/:base_id/create',
      name: 'knowledge-base-create',
      component: () => import('../views/KnowledgeBaseManager/KnowledgeBaseCreate.vue')
    }
  ]
})

// 定义白名单路由
const whiteList = ['/login']

// 定义检查管理员权限的函数
async function checkAdminAccess(): Promise<boolean> {


  const accessToken = localStorage.getItem('token')
  if (!accessToken) return false
  const baseURL = import.meta.env.VITE_APP_BASE_URL;
  try {
    const response = await fetch(baseURL+'/v1/api/mark/account/me', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    })
    if (response.ok) {
      // const result = await response.json()
      return true
    }
  } catch (error) {
    console.error('Error verifying admin access:', error)
  }
  return false

}

// 路由守卫
router.beforeEach(async (to, from, next) => {
  // 1. 检查是否是白名单路由
  if (whiteList.includes(to.path)) {
    next()
    return
  }

  // 2. 检查权限
  const hasAdminAccess = await checkAdminAccess()
  if (!hasAdminAccess) {
    next({ name: 'login', query: { redirect: to.fullPath } })
    return
  }

  next()
})

export default router
