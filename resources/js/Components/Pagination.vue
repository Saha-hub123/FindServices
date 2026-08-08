<script setup>
import { Link } from '@inertiajs/vue3';

defineProps({
    links: Array
});
</script>

<template>
    <div v-if="links.length > 3">
        <div class="flex flex-wrap items-center justify-center gap-1 -mb-1">
            <template v-for="(link, key) in links" :key="key">
                
                <div v-if="link.url === null" 
                     class="mr-1 mb-1 px-3 py-2 text-sm leading-4 text-gray-400 border border-gray-100 rounded-lg bg-white"
                     v-html="link.label">
                </div>

                <Link v-else 
                      class="mr-1 mb-1 px-3 py-2 text-sm leading-4 border rounded-lg hover:bg-white focus:border-blue-500 focus:text-blue-500 transition duration-150 ease-in-out"
                      :class="{ 'bg-blue-600 text-white border-blue-600 hover:bg-blue-700': link.active, 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50': !link.active }" 
                      :href="link.url">
                    <span v-html="link.label"></span>
                </Link>

            </template>
        </div>
    </div>
</template>