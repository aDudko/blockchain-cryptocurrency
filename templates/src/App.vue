<template>
    <div>
        <nav class="nav nav-pills mb-3">
            <router-link to="/" class="nav-link">Wallet & Node</router-link>
            <router-link to="/network" class="nav-link">Network</router-link>
        </nav>
        <router-view></router-view>
    </div>
</template>

<script>
export default {
    name: "App",
};
</script>