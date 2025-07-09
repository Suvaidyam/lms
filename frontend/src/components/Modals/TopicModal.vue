<template>
	<Dialog v-model="show" :options="{
		title: TopicDetail ? __('Edit Topic') : __('Add Topic'),
		size: 'lg',
		actions: [
			{
				label: TopicDetail ? __('Edit') : __('Create'),
				variant: 'solid',
				onClick: (close) =>
					TopicDetail ? editTopic(close) : addTopic(close),
			},
		],
	}">
		<template #body-content>
			<div class="space-y-4 text-base">
				<FormControl label="Title" v-model="Topic.title" :required="true" />
				<Switch size="sm" :label="__('SCORM Package')"
					:description="__('Enable this only if you want to upload a SCORM package as a Topic.')"
					v-model="Topic.is_scorm_package" />
				<div v-if="Topic.is_scorm_package">
					<FileUploader v-if="!Topic.scorm_package" :fileTypes="['.zip']" :validateFile="validateFile"
						@success="(file) => (Topic.scorm_package = file)">
						<template v-slot="{ file, progress, uploading, openFileSelector }">
							<div class="mb-4">
								<Button @click="openFileSelector" :loading="uploading">
									{{ uploading ? `Uploading ${progress}%` : 'Upload a zip file' }}
								</Button>
							</div>
						</template>
					</FileUploader>
					<div v-else>
						<div class="flex items-center">
							<div class="border rounded-md p-2 mr-2">
								<FileText class="h-5 w-5 stroke-1.5 text-gray-700" />
							</div>
							<div class="flex flex-col">
								<span>{{ Topic.scorm_package.file_name }}</span>
								<span class="text-sm text-gray-500 mt-1">
									{{ getFileSize(Topic.scorm_package.file_size) }}
								</span>
							</div>
							<X @click="() => (Topic.scorm_package = null)"
								class="bg-gray-200 rounded-md cursor-pointer stroke-1.5 w-5 h-5 p-1 ml-4" />
						</div>
					</div>
				</div>
			</div>
		</template>
	</Dialog>
</template>

<script setup>
import {
	Button,
	createResource,
	Dialog,
	FileUploader,
	FormControl,
	Switch,
} from 'frappe-ui'
import { defineModel, onMounted, reactive, watch } from 'vue'
import { showToast, getFileSize } from '@/utils/'
import { capture } from '@/telemetry'
import { FileText, X } from 'lucide-vue-next'
import { useSettings } from '@/stores/settings'

const show = defineModel()
const outline = defineModel('outline')
const settingsStore = useSettings()

const props = defineProps({
	course: {
		type: String,
		required: true,
	},
	semester: {
		type: String,
		required: true,
	},
	module: {
		type: String,
		required: true,
	},
	TopicDetail: {
		type: Object,
		default: null,
	},
})




const Topic = reactive({
	title: '',
	is_scorm_package: 0,
	scorm_package: null,
})

const TopicResource = createResource({
	url: 'lms.lms.api.upsert_Topic',
	makeParams() {
		return {
			title: Topic.title,
			course: props.course,
			semester: props.semester,
			module: props.module,
			is_scorm_package: Topic.is_scorm_package,
			scorm_package: Topic.scorm_package,
			name: props.TopicDetail?.name,
		}
	},
})

const TopicReference = createResource({
	url: 'frappe.client.insert',
	makeParams(values) {
		return {
			doc: {
				doctype: 'Course Topic Child',
				topic: values.name,
				parent: props.module,
				parenttype: 'Course Module',
				parentfield: 'topics',
			},
		}
	},
})

const addTopic = async (close) => {
	TopicResource.submit(
		{},
		{
			validate: validateTopic,
			onSuccess(data) {
				capture('Topic_created')
				TopicReference.submit(
					{ name: data.name },
					{
						onSuccess() {
							cleanTopic()
							if (!settingsStore.onboardingDetails.data?.is_onboarded) {
								settingsStore.onboardingDetails.reload()
							}
							outline.value.reload()
							showToast(__('Success'), __('Topic added successfully'), 'check')
							close()
						},
						onError(err) {
							showToast(__('Error'), err.messages?.[0] || err, 'x')
						},
					}
				)
			},
			onError(err) {
				showToast(__('Error'), err.messages?.[0] || err, 'x')
			},
		}
	)
}

const editTopic = (close) => {
	TopicResource.submit(
		{},
		{
			validate: validateTopic,
			onSuccess() {
				outline.value.reload()
				showToast(__('Success'), __('Topic updated successfully'), 'check')
				close()
			},
			onError(err) {
				showToast(__('Error'), err.messages?.[0] || err, 'x')
			},
		}
	)
}

const validateTopic = () => {
	if (!Topic.title) {
		return __('Topic Title is required')
	}
	if (Topic.is_scorm_package && !Topic.scorm_package) {
		return __('Please upload a SCORM package')
	}
	return true
}

const cleanTopic = () => {
	Topic.title = ''
	Topic.is_scorm_package = 0
	Topic.scorm_package = null
}

watch(
	() => props.TopicDetail,
	(newTopic) => {
		if (newTopic) {
			Topic.title = newTopic.title || ''
			Topic.is_scorm_package = newTopic.is_scorm_package || 0
			Topic.scorm_package = newTopic.scorm_package || null
		} else {
			cleanTopic()
		}
	},
	{ immediate: true }
)

const validateFile = (file) => {
	let extension = file.name.split('.').pop().toLowerCase()
	if (extension !== 'zip') {
		return __('Only zip files are allowed')
	}
}

onMounted(() => {

	capture('TopicModal_loaded', { course: props.course, TopicDetail: props.TopicDetail })
	console.log('TopicModal loaded with props:', "props");
})
</script>
